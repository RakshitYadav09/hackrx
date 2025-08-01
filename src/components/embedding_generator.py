"""
Embedding Generator Component for converting text to vector embeddings
"""
import logging
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Handles text-to-vector embedding conversion"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.embedding_dimension = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            self.model = SentenceTransformer(self.model_name)
            # Get embedding dimension by encoding a test sentence
            test_embedding = self.model.encode(["test"])
            self.embedding_dimension = test_embedding.shape[1]
            logger.info(f"Loaded embedding model {self.model_name} with dimension {self.embedding_dimension}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise Exception(f"Failed to load embedding model: {str(e)}")
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        try:
            if not texts:
                return np.array([])
            
            embeddings = self.model.encode(texts, show_progress_bar=True)
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise Exception(f"Failed to generate embeddings: {str(e)}")
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for a single query"""
        try:
            embedding = self.model.encode([query])
            return embedding[0]  # Return single embedding vector
            
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {str(e)}")
            raise Exception(f"Failed to generate query embedding: {str(e)}")
    
    def process_chunks_for_embedding(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process document chunks and add embeddings"""
        try:
            # Extract text content from chunks
            texts = [chunk["content"] for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.generate_embeddings(texts)
            
            # Add embeddings to chunks
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                processed_chunk = chunk.copy()
                processed_chunk["embedding"] = embeddings[i]
                processed_chunks.append(processed_chunk)
            
            logger.info(f"Processed {len(processed_chunks)} chunks with embeddings")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Failed to process chunks for embedding: {str(e)}")
            raise Exception(f"Failed to process chunks for embedding: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings"""
        return self.embedding_dimension
