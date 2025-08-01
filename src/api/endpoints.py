"""
API endpoints for the Query Retrieval System
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import asyncio
import time

from .models import QueryRequest, QueryResponse, ErrorResponse, HealthResponse
from .auth import get_current_user
from ..components import QueryRetrievalSystem
from ..config import settings

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["Query Retrieval"])

# Global system instance (will be initialized on startup)
query_system: QueryRetrievalSystem = None

def get_query_system() -> QueryRetrievalSystem:
    """Get the global query system instance"""
    global query_system
    if query_system is None:
        # Initialize system with configuration
        config = {
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "embedding_model": settings.embedding_model,
            "use_pinecone": settings.use_pinecone,
            "pinecone_api_key": settings.pinecone_api_key,
            "pinecone_environment": settings.pinecone_environment,
            "pinecone_index_name": settings.pinecone_index_name,
            "gemini_api_key": settings.gemini_api_key,
            "llm_model": settings.llm_model,
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature
        }
        query_system = QueryRetrievalSystem(config)
        logger.info("Initialized global query system")
    
    return query_system

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        system = get_query_system()
        system_status = system.get_system_status()
        
        return HealthResponse(
            status="healthy",
            components=system_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )

@router.post("/hackrx/run", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> QueryResponse:
    """
    Process document and answer questions
    
    This endpoint:
    1. Downloads and processes the PDF document
    2. Creates vector embeddings for document chunks
    3. Processes each question using semantic search and LLM evaluation
    4. Returns structured answers with citations
    """
    start_time = time.time()
    
    try:
        logger.info(f"Processing request with {len(request.questions)} questions")
        
        # Validate inputs
        if not request.questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one question is required"
            )
        
        if len(request.questions) > 20:  # Reasonable limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 20 questions allowed per request"
            )
        
        # Get system instance
        system = get_query_system()
        
        # Process document and questions
        result = await system.process_document_and_questions(
            document_url=str(request.documents),
            questions=request.questions
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Request processed successfully in {processing_time:.2f} seconds")
        
        return QueryResponse(**result)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Request processing failed: {str(e)}")
        processing_time = time.time() - start_time
        
        # Return appropriate error response
        if "download" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to download document: {str(e)}"
            )
        elif "parse" in str(e).lower() or "extract" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to process document: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal processing error: {str(e)}"
            )

@router.get("/status")
async def get_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get detailed system status"""
    try:
        system = get_query_system()
        return {
            "status": "operational",
            "timestamp": time.time(),
            "components": system.get_system_status(),
            "configuration": {
                "use_pinecone": settings.use_pinecone,
                "embedding_model": settings.embedding_model,
                "llm_model": settings.llm_model,
                "chunk_size": settings.chunk_size,
                "chunk_overlap": settings.chunk_overlap
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status: {str(e)}"
        )

@router.post("/webhook/test")
async def webhook_test(request: QueryRequest):
    """
    Webhook endpoint for testing - No authentication required
    
    This endpoint allows external systems to test the API without authentication.
    Perfect for automated testing and submission validation.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Webhook test request with {len(request.questions)} questions")
        
        # Validate inputs
        if not request.questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one question is required"
            )
        
        if len(request.questions) > 20:  # Reasonable limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 20 questions allowed per request"
            )
        
        # Get system instance
        system = get_query_system()
        
        # Process document and questions
        result = await system.process_document_and_questions(
            document_url=str(request.documents),
            questions=request.questions
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Webhook test processed successfully in {processing_time:.2f} seconds")
        
        # Add webhook-specific metadata
        result.update({
            "webhook": True,
            "processing_time": processing_time,
            "timestamp": time.time(),
            "request_id": f"webhook_{int(time.time() * 1000)}"
        })
        
        return QueryResponse(**result)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Webhook test failed: {str(e)}")
        processing_time = time.time() - start_time
        
        # Return appropriate error response
        if "download" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to download document: {str(e)}"
            )
        elif "parse" in str(e).lower() or "extract" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to process document: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal processing error: {str(e)}"
            )
