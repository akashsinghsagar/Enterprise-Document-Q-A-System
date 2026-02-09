"""
RAG Pipeline for Document Q&A System

Handles retrieval-augmented generation workflow:
1. Query embedding
2. Semantic search in vector store
3. Context construction
4. LLM-based answer generation
"""

import os
from typing import List, Dict, Optional, Tuple

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document

from app.utils import config, logger
from app.prompts import get_rag_prompt, format_context, validate_answer


class Retriever:
    """
    Handles semantic search and document retrieval from vector store.
    
    Provides flexible retrieval with configurable similarity search parameters.
    """
    
    def __init__(self, vector_store: FAISS, top_k: int = 4):
        """
        Initialize retriever with vector store.
        
        Args:
            vector_store: FAISS vector store instance
            top_k: Number of top documents to retrieve
        """
        self.vector_store = vector_store
        self.top_k = top_k
        self.logger = logger
    
    def retrieve(
        self, 
        query: str, 
        top_k: Optional[int] = None
    ) -> List[Document]:
        """
        Retrieve most relevant documents for a query.
        
        Args:
            query: User question or search query
            top_k: Override default number of documents to retrieve
            
        Returns:
            List[Document]: Retrieved document chunks with metadata
        """
        k = top_k or self.top_k
        
        self.logger.info(f"Retrieving top {k} documents for query: {query[:100]}...")
        
        try:
            # Perform similarity search
            documents = self.vector_store.similarity_search(
                query=query,
                k=k
            )
            
            self.logger.info(f"Retrieved {len(documents)} documents")
            
            # Log retrieved document sources for debugging
            for i, doc in enumerate(documents, 1):
                source = doc.metadata.get('source', 'Unknown')
                chunk_id = doc.metadata.get('chunk_id', 'N/A')
                self.logger.debug(f"Doc {i}: {source} (chunk {chunk_id})")
            
            return documents
            
        except Exception as e:
            self.logger.error(f"Retrieval error: {e}")
            raise
    
    def retrieve_with_scores(
        self, 
        query: str, 
        top_k: Optional[int] = None
    ) -> List[Tuple[Document, float]]:
        """
        Retrieve documents with similarity scores.
        
        Args:
            query: User question or search query
            top_k: Override default number of documents to retrieve
            
        Returns:
            List[Tuple[Document, float]]: Document-score pairs
        """
        k = top_k or self.top_k
        
        self.logger.info(
            f"Retrieving top {k} documents with scores for query: {query[:100]}..."
        )
        
        try:
            # Perform similarity search with scores
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query=query,
                k=k
            )
            
            self.logger.info(f"Retrieved {len(docs_with_scores)} documents with scores")
            
            # Log scores for debugging
            for i, (doc, score) in enumerate(docs_with_scores, 1):
                source = doc.metadata.get('source', 'Unknown')
                self.logger.debug(f"Doc {i}: {source} (score: {score:.4f})")
            
            return docs_with_scores
            
        except Exception as e:
            self.logger.error(f"Retrieval with scores error: {e}")
            raise


class Generator:
    """
    Handles LLM-based answer generation.
    
    Uses NVIDIA LLM endpoints via OpenAI-compatible API.
    """
    
    def __init__(self, temperature: float = 0.0):
        """
        Initialize generator with NVIDIA LLM.
        
        Args:
            temperature: LLM temperature (0.0 for deterministic, higher for creative)
        """
        self.logger = logger
        
        # Initialize NVIDIA LLM using OpenAI-compatible endpoint
        self.llm = ChatOpenAI(
            model=config.nvidia_llm_model,
            openai_api_key=config.nvidia_api_key,
            openai_api_base=config.nvidia_base_url,
            temperature=temperature,
            max_tokens=512
        )
        
        self.prompt = get_rag_prompt()
    
    def generate(
        self, 
        context: str, 
        question: str
    ) -> str:
        """
        Generate answer from context and question.
        
        Args:
            context: Retrieved and formatted document context
            question: User's question
            
        Returns:
            str: Generated answer
        """
        self.logger.info(f"Generating answer for question: {question[:100]}...")
        
        try:
            # Format prompt with context and question
            formatted_prompt = self.prompt.format(
                context=context,
                question=question
            )
            
            # Generate answer using LLM
            response = self.llm.invoke(formatted_prompt)
            
            # Extract answer from response
            answer = response.content if hasattr(response, 'content') else str(response)
            
            self.logger.info(f"Generated answer: {answer[:100]}...")
            
            return answer.strip()
            
        except Exception as e:
            self.logger.error(f"Generation error: {e}")
            raise


class RAGPipeline:
    """
    Complete RAG pipeline orchestrating retrieval and generation.
    
    Provides high-level interface for question answering with metadata.
    """
    
    def __init__(
        self, 
        vector_store_path: Optional[str] = None,
        top_k: int = 4,
        temperature: float = 0.0
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            vector_store_path: Path to FAISS vector store
            top_k: Number of documents to retrieve
            temperature: LLM temperature
            
        Raises:
            FileNotFoundError: If vector store doesn't exist
        """
        self.logger = logger
        self.top_k = top_k
        
        # Load vector store
        store_path = vector_store_path or config.vector_store_path
        
        # Check if path exists and contains index files
        if not os.path.exists(store_path):
            raise FileNotFoundError(
                f"Vector store directory not found at {store_path}. "
                "Please upload and ingest documents first to create embeddings."
            )
        
        # Check if FAISS index file exists
        index_path = os.path.join(store_path, "index.faiss")
        if not os.path.exists(index_path):
            raise FileNotFoundError(
                f"FAISS index not found. No documents ingested yet. "
                "Please upload a PDF to create the vector store first."
            )
        
        self.logger.info(f"Loading vector store from {store_path}")
        
        try:
            # Initialize embeddings
            embeddings = OpenAIEmbeddings(
                model=config.nvidia_embedding_model,
                openai_api_key=config.nvidia_api_key,
                openai_api_base=config.nvidia_base_url,
                check_embedding_ctx_length=False
            )
            
            # Load FAISS vector store
            self.vector_store = FAISS.load_local(
                store_path,
                embeddings=embeddings,
                allow_dangerous_deserialization=True
            )
            
            # Initialize retriever and generator
            self.retriever = Retriever(self.vector_store, top_k=top_k)
            self.generator = Generator(temperature=temperature)
            
            self.logger.info("RAG pipeline initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to load vector store: {e}")
            raise FileNotFoundError(
                f"Error loading vector store: {str(e)}. "
                "The vector store may be corrupted. "
                "Please delete the data/vector_store folder and re-upload documents."
            )
    
    def query(
        self,
        question: str,
        return_sources: bool = True
    ) -> Dict:
        """
        Execute RAG pipeline for a question.
        
        Args:
            question: User's question
            return_sources: Whether to include source documents in response
            
        Returns:
            dict: Response containing answer, sources, and metadata
        """
        self.logger.info(f"Processing query: {question}")
        
        try:
            # Step 1: Retrieve relevant documents
            documents = self.retriever.retrieve(question)
            
            if not documents:
                self.logger.warning("No documents retrieved")
                return {
                    'question': question,
                    'answer': 'Answer not available in the document.',
                    'answer_available': False,
                    'sources': [],
                    'num_sources': 0
                }
            
            # Step 2: Format context
            context = format_context(documents)
            
            # Step 3: Generate answer
            raw_answer = self.generator.generate(context, question)
            
            # Step 4: Validate answer
            answer_info = validate_answer(raw_answer)
            
            # Step 5: Prepare response
            response = {
                'question': question,
                'answer': answer_info['answer'],
                'answer_available': answer_info['answer_available'],
                'confidence': answer_info['confidence'],
                'num_sources': len(documents)
            }
            
            # Add source information if requested
            if return_sources:
                sources = []
                for doc in documents:
                    sources.append({
                        'content': doc.page_content[:200] + '...',  # Preview
                        'source': doc.metadata.get('source', 'Unknown'),
                        'page': doc.metadata.get('page', 'N/A'),
                        'chunk_id': doc.metadata.get('chunk_id', 'N/A')
                    })
                response['sources'] = sources
            
            self.logger.info(
                f"Query processed successfully. "
                f"Answer available: {answer_info['answer_available']}"
            )
            
            return response
        except Exception as e:
            self.logger.error(f"RAG pipeline error: {e}")
            return {
                'question': question,
                'answer': f'Error processing query: {str(e)}',
                'answer_available': False,
                'sources': [],
                'num_sources': 0,
                'error': str(e)
            }
    
    def batch_query(self, questions: List[str]) -> List[Dict]:
        """
        Process multiple questions in batch.
        
        Args:
            questions: List of user questions
            
        Returns:
            List[dict]: List of responses for each question
        """
        self.logger.info(f"Processing batch of {len(questions)} questions")
        
        results = []
        for i, question in enumerate(questions, 1):
            self.logger.info(f"Processing question {i}/{len(questions)}")
            result = self.query(question)
            results.append(result)
        
        return results
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store.
        
        Returns:
            dict: Vector store statistics
        """
        try:
            # FAISS doesn't directly expose document count, so we estimate
            index_size = self.vector_store.index.ntotal if hasattr(
                self.vector_store, 'index'
            ) else 0
            
            return {
                'vector_store_path': config.vector_store_path,
                'estimated_documents': index_size,
                'top_k': self.top_k,
                'embedding_model': config.nvidia_embedding_model,
                'llm_model': config.nvidia_llm_model
            }
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}
