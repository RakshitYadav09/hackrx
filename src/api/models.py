"""
API Models for request and response schemas
"""
from typing import List
from pydantic import BaseModel, HttpUrl, Field

class QueryRequest(BaseModel):
    """Request model for the query endpoint"""
    documents: HttpUrl = Field(..., description="URL of the PDF document to process")
    questions: List[str] = Field(..., description="List of questions to answer", min_items=1)
    
    class Config:
        schema_extra = {
            "example": {
                "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
                "questions": [
                    "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
                    "What is the waiting period for pre-existing diseases (PED) to be covered?"
                ]
            }
        }

class QueryResponse(BaseModel):
    """Response model for the query endpoint"""
    answers: List[str] = Field(..., description="List of answers corresponding to the questions")
    
    class Config:
        schema_extra = {
            "example": {
                "answers": [
                    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
                    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered."
                ]
            }
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: str = Field(None, description="Detailed error information")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Document processing failed",
                "detail": "Failed to download PDF from the provided URL"
            }
        }

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    components: dict = Field(..., description="Component status details")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "components": {
                    "pdf_processor": "ready",
                    "embedding_generator": {
                        "model": "all-MiniLM-L6-v2",
                        "dimension": 384
                    },
                    "vector_db": {
                        "type": "FAISS",
                        "status": "ready"
                    },
                    "llm_processor": {
                        "model": "gpt-4-turbo-preview",
                        "status": "ready"
                    }
                }
            }
        }
