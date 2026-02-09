"""
Document Ingestion Pipeline for Enterprise RAG System

Handles PDF document processing, text extraction, chunking, 
embedding generation, and FAISS vector store creation.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from app.utils import config, logger, validate_pdf_file, sanitize_filename, get_file_metadata


class DocumentProcessor:
    """
    Handles PDF document processing and text extraction.
    
    Provides robust PDF reading with error handling and text cleaning.
    """
    
    def __init__(self):
        """Initialize the document processor."""
        self.logger = logger
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, dict]:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (extracted text, metadata dictionary)
            
        Raises:
            ValueError: If PDF is invalid or cannot be read
            Exception: For other PDF processing errors
        """
        if not validate_pdf_file(pdf_path):
            raise ValueError(f"Invalid PDF file: {pdf_path}")
        
        try:
            self.logger.info(f"Extracting text from PDF: {pdf_path}")
            
            pdf_reader = PdfReader(pdf_path)
            total_pages = len(pdf_reader.pages)
            
            text_content = []
            page_metadata = []
            
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_content.append(page_text)
                        page_metadata.append({
                            'page': page_num,
                            'char_count': len(page_text)
                        })
                except Exception as e:
                    self.logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    continue
            
            full_text = "\n\n".join(text_content)
            
            metadata = {
                'source': os.path.basename(pdf_path),
                'total_pages': total_pages,
                'extracted_pages': len(text_content),
                'total_characters': len(full_text),
                'file_path': pdf_path
            }
            
            self.logger.info(
                f"Extracted {len(full_text)} characters from "
                f"{len(text_content)}/{total_pages} pages"
            )
            
            return full_text, metadata
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text for better embeddings.
        
        Args:
            text: Raw extracted text
            
        Returns:
            str: Cleaned and normalized text
        """
        import re
        
        # Remove page numbers and headers/footers
        text = re.sub(r'^\s*-?\s*\d+\s*-?\s*$', '', text, flags=re.MULTILINE)
        
        # Fix common PDF extraction issues
        text = text.replace('\n', ' ')  # Replace newlines with spaces first
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        
        # Add proper sentence spacing after periods
        text = re.sub(r'(?<=[.!?])\s+(?=[A-Z])', '. ', text)
        
        # Clean up broken words (e.g., "hus hold" -> "household")
        text = re.sub(r'(?<=[a-z])\s+(?=[a-z])', '', text)
        
        # Fix spacing issues around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)
        
        return text.strip()


class TextChunker:
    """
    Handles intelligent text chunking with semantic awareness.
    
    Uses RecursiveCharacterTextSplitter configured for optimal retrieval
    with larger chunks that preserve document context and semantic meaning.
    """
    
    def __init__(
        self, 
        chunk_size: int = 1200, 
        chunk_overlap: int = 300
    ):
        """
        Initialize text chunker with semantic-aware parameters.
        
        Args:
            chunk_size: Maximum size of each chunk in characters (1200 optimal for RAG)
            chunk_overlap: Number of overlapping characters between chunks (300 for continuity)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.logger = logger
        
        # Semantic-aware splitting: respect sentence and paragraph boundaries
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            # Split in order of importance: paragraphs > sentences > words > chars
            separators=[
                "\n\n",      # Paragraph boundaries
                "\n",        # Line breaks
                ". ",         # Sentence boundaries
                "! ",         # Exclamation marks
                "? ",         # Questions
                "; ",         # Semicolons
                ", ",         # Commas (loose boundary)
                " ",          # Word boundaries
                ""            # Character level (fallback)
            ]
        )
    
    def chunk_text(
        self, 
        text: str, 
        metadata: dict
    ) -> List[Document]:
        """
        Split text into semantic chunks with enhanced metadata.
        
        Args:
            text: Text to chunk
            metadata: Document metadata to attach to each chunk
            
        Returns:
            List[Document]: List of LangChain Document objects with semantically coherent chunks
        """
        self.logger.info(
            f"Semantic chunking: {len(text)} chars "
            f"(size={self.chunk_size}, overlap={self.chunk_overlap})"
        )
        
        # Split text into chunks respecting semantic boundaries
        chunks = self.text_splitter.split_text(text)
        
        # Create Document objects with enhanced metadata
        documents = []
        for i, chunk in enumerate(chunks):
            # Clean up chunk
            chunk = chunk.strip()
            if not chunk or len(chunk) < 50:  # Skip very small chunks
                continue
            
            doc_metadata = metadata.copy()
            doc_metadata['chunk_id'] = i
            doc_metadata['chunk_size'] = len(chunk)
            doc_metadata['chunk_order'] = i
            # Add first 100 chars as summary
            doc_metadata['chunk_preview'] = chunk[:100].replace('\n', ' ')
            
            documents.append(Document(
                page_content=chunk,
                metadata=doc_metadata
            ))
        
        self.logger.info(
            f"Created {len(documents)} semantic chunks "
            f"(avg size: {sum(len(d.page_content) for d in documents) // max(len(documents), 1)} chars)"
        )
        return documents


class VectorStoreManager:
    """
    Manages FAISS vector store operations.
    
    Handles embedding generation, vector store creation, and persistence.
    """
    
    def __init__(self):
        """Initialize vector store manager with NVIDIA embeddings."""
        self.logger = logger
        self.vector_store_path = config.vector_store_path
        
        # Initialize NVIDIA embeddings using OpenAI-compatible endpoint
        self.embeddings = OpenAIEmbeddings(
            model=config.nvidia_embedding_model,
            openai_api_key=config.nvidia_api_key,
            openai_api_base=config.nvidia_base_url,
            check_embedding_ctx_length=False
        )
        
        self.vector_store: Optional[FAISS] = None
    
    def create_vector_store(
        self, 
        documents: List[Document]
    ) -> FAISS:
        """
        Create a new FAISS vector store from documents.
        
        Args:
            documents: List of Document objects to embed
            
        Returns:
            FAISS: Created vector store
            
        Raises:
            ValueError: If documents list is empty
        """
        if not documents:
            raise ValueError("Cannot create vector store from empty document list")
        
        self.logger.info(f"Creating vector store from {len(documents)} documents")
        
        try:
            # Create FAISS vector store with embeddings
            self.vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            
            self.logger.info("Vector store created successfully")
            return self.vector_store
            
        except Exception as e:
            self.logger.error(f"Error creating vector store: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to existing vector store.
        
        Args:
            documents: List of Document objects to add
            
        Raises:
            ValueError: If vector store doesn't exist
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Create one first.")
        
        if not documents:
            self.logger.warning("No documents to add")
            return
        
        self.logger.info(f"Adding {len(documents)} documents to vector store")
        
        try:
            self.vector_store.add_documents(documents)
            self.logger.info("Documents added successfully")
            
        except Exception as e:
            self.logger.error(f"Error adding documents: {e}")
            raise
    
    def save_vector_store(self, path: Optional[str] = None) -> None:
        """
        Persist vector store to disk.
        
        Args:
            path: Optional custom path for saving. Uses config default if None.
            
        Raises:
            ValueError: If vector store doesn't exist
        """
        if self.vector_store is None:
            raise ValueError("No vector store to save")
        
        save_path = path or self.vector_store_path
        
        self.logger.info(f"Saving vector store to {save_path}")
        
        try:
            # Ensure directory exists
            Path(save_path).mkdir(parents=True, exist_ok=True)
            
            # Save the vector store
            self.vector_store.save_local(save_path)
            
            self.logger.info("Vector store saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving vector store: {e}")
            raise
    
    def load_vector_store(self, path: Optional[str] = None) -> FAISS:
        """
        Load vector store from disk.
        
        Args:
            path: Optional custom path for loading. Uses config default if None.
            
        Returns:
            FAISS: Loaded vector store
            
        Raises:
            FileNotFoundError: If vector store doesn't exist at path
        """
        load_path = path or self.vector_store_path
        
        if not os.path.exists(load_path):
            raise FileNotFoundError(f"Vector store not found at {load_path}")
        
        index_path = os.path.join(load_path, "index.faiss")
        if not os.path.exists(index_path):
            raise FileNotFoundError(
                f"FAISS index not found at {index_path}"
            )
        
        self.logger.info(f"Loading vector store from {load_path}")
        
        try:
            self.vector_store = FAISS.load_local(
                load_path,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            self.logger.info("Vector store loaded successfully")
            return self.vector_store
            
        except Exception as e:
            self.logger.error(f"Error loading vector store: {e}")
            raise


class IngestionPipeline:
    """
    End-to-end document ingestion pipeline.
    
    Orchestrates document processing, chunking, embedding, and vector store creation.
    """
    
    def __init__(self):
        """Initialize the ingestion pipeline with all components."""
        self.logger = logger
        self.doc_processor = DocumentProcessor()
        self.text_chunker = TextChunker(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
        self.vector_store_manager = VectorStoreManager()
    
    def ingest_pdf(self, pdf_path: str) -> dict:
        """
        Ingest a single PDF document into the vector store.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            dict: Ingestion results with statistics
        """
        self.logger.info(f"Starting ingestion of {pdf_path}")
        
        try:
            # Step 1: Extract text from PDF
            text, metadata = self.doc_processor.extract_text_from_pdf(pdf_path)
            
            # Step 2: Clean text
            cleaned_text = self.doc_processor.clean_text(text)
            
            # Step 3: Chunk text
            chunks = self.text_chunker.chunk_text(cleaned_text, metadata)
            
            # Step 4: Create or update vector store
            try:
                # Try to load existing vector store
                self.vector_store_manager.load_vector_store()
                self.vector_store_manager.add_documents(chunks)
            except FileNotFoundError:
                # Create new vector store if doesn't exist
                self.vector_store_manager.create_vector_store(chunks)
            
            # Step 5: Save vector store
            self.vector_store_manager.save_vector_store()
            
            result = {
                'status': 'success',
                'document': metadata['source'],
                'chunks_created': len(chunks),
                'total_characters': metadata['total_characters'],
                'pages_processed': metadata['extracted_pages']
            }
            
            self.logger.info(f"Successfully ingested {pdf_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Ingestion failed for {pdf_path}: {e}")
            return {
                'status': 'error',
                'document': os.path.basename(pdf_path),
                'error': str(e)
            }
    
    def ingest_directory(self, directory_path: str) -> List[dict]:
        """
        Ingest all PDF files from a directory.
        
        Args:
            directory_path: Path to directory containing PDFs
            
        Returns:
            List[dict]: List of ingestion results for each file
        """
        self.logger.info(f"Ingesting PDFs from directory: {directory_path}")
        
        pdf_files = list(Path(directory_path).glob("*.pdf"))
        
        if not pdf_files:
            self.logger.warning(f"No PDF files found in {directory_path}")
            return []
        
        results = []
        for pdf_file in pdf_files:
            result = self.ingest_pdf(str(pdf_file))
            results.append(result)
        
        # Summary statistics
        successful = sum(1 for r in results if r['status'] == 'success')
        self.logger.info(
            f"Directory ingestion complete: {successful}/{len(results)} successful"
        )
        
        return results
