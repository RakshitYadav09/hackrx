"""
Main FastAPI application
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.api import router
from src.utils import setup_logging
from src.config import settings

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting LLM-Powered Query Retrieval System")
    
    # Validate configuration
    if not settings.gemini_api_key:
        logger.warning("Gemini API key not configured")
    
    if settings.use_pinecone and not settings.pinecone_api_key:
        logger.warning("Pinecone enabled but API key not configured, falling back to FAISS")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")

# Create FastAPI app
app = FastAPI(
    title="LLM-Powered Intelligent Query-Retrieval System",
    description="""
    An intelligent document processing and query answering system that:
    
    - Downloads and processes PDF documents
    - Creates semantic embeddings for document content
    - Answers natural language questions using LLM-powered analysis
    - Provides explainable answers with document citations
    
    **Features:**
    - PDF parsing and chunking
    - Vector similarity search (FAISS/Pinecone)
    - LLM-powered query understanding and response generation
    - Structured JSON responses with citations
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred while processing your request"
        }
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LLM-Powered Intelligent Query-Retrieval System",
        "status": "running",
        "docs": "/docs",
        "api_base": "/api/v1"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
