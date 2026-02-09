"""
FastAPI Backend for Enterprise Document Q&A System

Provides REST API endpoints for:
- Document upload and ingestion
- Question answering
- System health and statistics
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.utils import config, logger, sanitize_filename
from app.ingest import IngestionPipeline
from app.rag_pipeline import RAGPipeline


# ============================================================================
# Pydantic Models for Request/Response
# ============================================================================

class QuestionRequest(BaseModel):
    """Request model for question answering."""
    question: str = Field(..., min_length=1, description="User's question")
    return_sources: bool = Field(
        default=True, 
        description="Include source documents in response"
    )


class QuestionResponse(BaseModel):
    """Response model for question answering."""
    question: str
    answer: str
    answer_available: bool
    confidence: Optional[str] = None
    num_sources: int
    sources: Optional[List[dict]] = None


class UploadResponse(BaseModel):
    """Response model for document upload."""
    status: str
    message: str
    filename: str
    details: Optional[dict] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    message: str
    vector_store_exists: bool


class StatsResponse(BaseModel):
    """Response model for system statistics."""
    vector_store_stats: dict
    config: dict


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Enterprise Document Q&A System",
    description="RAG-based document Q&A system with NVIDIA AI endpoints",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for cross-origin requests (needed for Streamlit UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Global State
# ============================================================================

# Initialize RAG pipeline (lazy loading)
rag_pipeline: Optional[RAGPipeline] = None
ingestion_pipeline = IngestionPipeline()


def get_rag_pipeline() -> RAGPipeline:
    """
    Get or initialize RAG pipeline.
    
    Returns:
        RAGPipeline: Initialized pipeline instance
        
    Raises:
        HTTPException: If vector store doesn't exist
    """
    global rag_pipeline
    
    if rag_pipeline is None:
        try:
            rag_pipeline = RAGPipeline(
                top_k=config.top_k,
                temperature=0.0
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="Vector store not found. Please upload and ingest documents first."
            )
    
    return rag_pipeline


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Enterprise Document Q&A System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Verifies API is running and checks vector store status.
    """
    vector_store_exists = os.path.exists(config.vector_store_path)
    
    if vector_store_exists:
        status = "healthy"
        message = "API is running. Vector store is available."
    else:
        status = "degraded"
        message = "API is running. Vector store not found - upload documents to enable Q&A."
    
    return HealthResponse(
        status=status,
        message=message,
        vector_store_exists=vector_store_exists
    )


@app.get("/stats", response_model=StatsResponse, tags=["System"])
async def get_stats():
    """
    Get system statistics.
    
    Returns configuration and vector store information.
    """
    try:
        pipeline = get_rag_pipeline()
        vector_store_stats = pipeline.get_stats()
    except HTTPException:
        vector_store_stats = {
            "status": "not_initialized",
            "message": "No documents ingested yet"
        }
    
    return StatsResponse(
        vector_store_stats=vector_store_stats,
        config={
            "chunk_size": config.chunk_size,
            "chunk_overlap": config.chunk_overlap,
            "top_k": config.top_k,
            "embedding_model": config.nvidia_embedding_model,
            "llm_model": config.nvidia_llm_model
        }
    )


@app.post("/upload", response_model=UploadResponse, tags=["Documents"])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload and ingest a PDF document.
    
    The document is saved, processed, chunked, embedded, and added to the vector store.
    Processing happens in the background after the upload completes.
    
    Args:
        file: PDF file to upload
        
    Returns:
        UploadResponse: Upload status and details
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    # Save uploaded file
    file_path = os.path.join(config.raw_docs_path, safe_filename)
    
    try:
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Uploaded file saved: {file_path}")
        
        # Start ingestion in background
        background_tasks.add_task(ingest_document_task, file_path)
        
        # Reset RAG pipeline to reload vector store after ingestion
        global rag_pipeline
        rag_pipeline = None
        
        return UploadResponse(
            status="success",
            message=f"Document uploaded successfully. Ingestion started in background.",
            filename=safe_filename,
            details={
                "file_size_bytes": os.path.getsize(file_path),
                "save_path": file_path
            }
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        # Clean up partial file if exists
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


def ingest_document_task(file_path: str):
    """
    Background task for document ingestion.
    
    Args:
        file_path: Path to the PDF file to ingest
    """
    try:
        logger.info(f"Starting background ingestion: {file_path}")
        result = ingestion_pipeline.ingest_pdf(file_path)
        
        if result['status'] == 'success':
            logger.info(f"Ingestion completed: {result}")
        else:
            logger.error(f"Ingestion failed: {result}")
            
    except Exception as e:
        logger.error(f"Background ingestion error: {e}")


@app.post("/query", response_model=QuestionResponse, tags=["Q&A"])
async def query_documents(request: QuestionRequest):
    """
    Ask a question about ingested documents.
    
    Uses RAG pipeline to retrieve relevant context and generate an answer.
    
    Args:
        request: Question request with query text and options
        
    Returns:
        QuestionResponse: Answer with sources and metadata
    """
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    try:
        # Get RAG pipeline
        pipeline = get_rag_pipeline()
        
        # Execute query
        result = pipeline.query(
            question=request.question,
            return_sources=request.return_sources
        )
        
        return QuestionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.post("/batch-query", response_model=List[QuestionResponse], tags=["Q&A"])
async def batch_query_documents(questions: List[str]):
    """
    Ask multiple questions in batch.
    
    Args:
        questions: List of question strings
        
    Returns:
        List[QuestionResponse]: List of answers
    """
    if not questions:
        raise HTTPException(
            status_code=400,
            detail="Questions list cannot be empty"
        )
    
    if len(questions) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 questions per batch request"
        )
    
    try:
        pipeline = get_rag_pipeline()
        results = pipeline.batch_query(questions)
        
        return [QuestionResponse(**result) for result in results]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch query error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing batch query: {str(e)}"
        )


@app.delete("/documents/{filename}", tags=["Documents"])
async def delete_document(filename: str):
    """
    Delete a document from storage.
    
    Note: This doesn't remove the document from the vector store.
    To rebuild the vector store, delete the vector_store directory and re-upload documents.
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        dict: Deletion status
    """
    safe_filename = sanitize_filename(filename)
    file_path = os.path.join(config.raw_docs_path, safe_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {safe_filename}"
        )
    
    try:
        os.remove(file_path)
        logger.info(f"Deleted document: {file_path}")
        
        return {
            "status": "success",
            "message": f"Document deleted: {safe_filename}",
            "note": "Vector store not updated. Rebuild if needed."
        }
        
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )


@app.get("/documents", tags=["Documents"])
async def list_documents():
    """
    List all uploaded documents.
    
    Returns:
        dict: List of document filenames with metadata
    """
    try:
        docs_path = Path(config.raw_docs_path)
        pdf_files = list(docs_path.glob("*.pdf"))
        
        documents = []
        for pdf_file in pdf_files:
            documents.append({
                "filename": pdf_file.name,
                "size_bytes": pdf_file.stat().st_size,
                "uploaded_at": pdf_file.stat().st_mtime
            })
        
        return {
            "total_documents": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )


# ============================================================================
# Application Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    logger.info("=" * 60)
    logger.info("Enterprise Document Q&A System API Starting")
    logger.info("=" * 60)
    logger.info(f"Vector Store Path: {config.vector_store_path}")
    logger.info(f"Raw Docs Path: {config.raw_docs_path}")
    logger.info(f"Embedding Model: {config.nvidia_embedding_model}")
    logger.info(f"LLM Model: {config.nvidia_llm_model}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    logger.info("Shutting down Enterprise Document Q&A System API")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=True,
        log_level=config.log_level.lower()
    )
