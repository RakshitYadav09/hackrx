"""
Configuration module for the LLM-Powered Query-Retrieval System
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Google Gemini Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Pinecone Configuration
    pinecone_api_key: Optional[str] = os.getenv("PINECONE_API_KEY")
    pinecone_environment: Optional[str] = os.getenv("PINECONE_ENVIRONMENT")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "hackrx-policy-index")
    
    # API Configuration
    api_token: str = os.getenv("API_TOKEN", "1fcad8c4ef8f698546d9a985893a9bfa5c60c562930511aa5c5e2ac8366de6fc")
    
    # Vector Database Configuration
    use_pinecone: bool = os.getenv("USE_PINECONE", "false").lower() == "true"
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # LLM Configuration
    llm_model: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.4"))
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()
