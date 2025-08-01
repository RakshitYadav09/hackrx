"""
Vector Database Manager supporting both FAISS and Pinecone
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss
import json
import os
from abc import ABC, abstractmethod

# Pinecone imports (optional)
try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

logger = logging.getLogger(__name__)

class VectorDBInterface(ABC):
    """Abstract interface for vector databases"""
    
    @abstractmethod
    def initialize(self, dimension: int) -> None:
        """Initialize the vector database"""
        pass
    
    @abstractmethod
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """Add vectors with metadata to the database"""
        pass
    
    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar vectors"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all vectors from the database"""
        pass

class FAISSVectorDB(VectorDBInterface):
    """FAISS-based vector database implementation"""
    
    def __init__(self):
        self.index = None
        self.metadata = []
        self.dimension = None
    
    def initialize(self, dimension: int) -> None:
        """Initialize FAISS index"""
        try:
            self.dimension = dimension
            # Use IndexFlatIP for inner product (cosine similarity)
            self.index = faiss.IndexFlatIP(dimension)
            self.metadata = []
            logger.info(f"Initialized FAISS index with dimension {dimension}")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {str(e)}")
            raise Exception(f"Failed to initialize FAISS index: {str(e)}")
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """Add vectors to FAISS index"""
        try:
            if self.index is None:
                raise Exception("FAISS index not initialized")
            
            # Normalize vectors for cosine similarity
            normalized_vectors = self._normalize_vectors(vectors)
            
            # Add to index
            self.index.add(normalized_vectors.astype(np.float32))
            
            # Store metadata
            self.metadata.extend(metadata)
            
            logger.info(f"Added {len(vectors)} vectors to FAISS index")
            
        except Exception as e:
            logger.error(f"Failed to add vectors to FAISS: {str(e)}")
            raise Exception(f"Failed to add vectors to FAISS: {str(e)}")
    
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar vectors in FAISS"""
        try:
            if self.index is None or self.index.ntotal == 0:
                return []
            
            # Normalize query vector
            normalized_query = self._normalize_vectors(query_vector.reshape(1, -1))
            
            # Search
            scores, indices = self.index.search(normalized_query.astype(np.float32), min(top_k, self.index.ntotal))
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx != -1 and idx < len(self.metadata):  # Valid index
                    results.append((self.metadata[idx], float(score)))
            
            logger.info(f"Found {len(results)} similar vectors")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search FAISS index: {str(e)}")
            raise Exception(f"Failed to search FAISS index: {str(e)}")
    
    def clear(self) -> None:
        """Clear FAISS index"""
        self.index = None
        self.metadata = []
        if self.dimension:
            self.initialize(self.dimension)
    
    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalize vectors for cosine similarity"""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return vectors / norms

class PineconeVectorDB(VectorDBInterface):
    """Pinecone-based vector database implementation"""
    
    def __init__(self, api_key: str, environment: str, index_name: str):
        if not PINECONE_AVAILABLE:
            raise Exception("Pinecone library not available. Install with: pip install pinecone-client")
        
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.pc = None
        self.index = None
        self.dimension = None
    
    def initialize(self, dimension: int) -> None:
        """Initialize Pinecone index"""
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=self.api_key)
            
            self.dimension = dimension
            
            # Check if index exists, create if it doesn't
            existing_indexes = self.pc.list_indexes().names()
            if self.index_name not in existing_indexes:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                logger.info(f"Created Pinecone index {self.index_name}")
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {str(e)}")
            raise Exception(f"Failed to initialize Pinecone index: {str(e)}")
    
    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """Add vectors to Pinecone index"""
        try:
            if self.index is None:
                raise Exception("Pinecone index not initialized")
            
            # Prepare vectors for upsert
            vectors_to_upsert = []
            for i, (vector, meta) in enumerate(zip(vectors, metadata)):
                # Convert metadata to string values (Pinecone requirement)
                string_metadata = {k: str(v) for k, v in meta.items() if k != 'embedding'}
                
                vectors_to_upsert.append({
                    "id": f"{meta.get('chunk_id', f'vec_{i}')}",
                    "values": vector.tolist(),
                    "metadata": string_metadata
                })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Added {len(vectors)} vectors to Pinecone index")
            
        except Exception as e:
            logger.error(f"Failed to add vectors to Pinecone: {str(e)}")
            raise Exception(f"Failed to add vectors to Pinecone: {str(e)}")
    
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar vectors in Pinecone"""
        try:
            if self.index is None:
                return []
            
            # Search
            results = self.index.query(
                vector=query_vector.tolist(),
                top_k=top_k,
                include_metadata=True
            )
            
            # Prepare results
            formatted_results = []
            for match in results.matches:
                metadata = dict(match.metadata)
                # Convert string values back to appropriate types
                if 'page_number' in metadata:
                    metadata['page_number'] = int(metadata['page_number'])
                if 'char_start' in metadata:
                    metadata['char_start'] = int(metadata['char_start'])
                if 'char_end' in metadata:
                    metadata['char_end'] = int(metadata['char_end'])
                
                formatted_results.append((metadata, float(match.score)))
            
            logger.info(f"Found {len(formatted_results)} similar vectors")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search Pinecone index: {str(e)}")
            raise Exception(f"Failed to search Pinecone index: {str(e)}")
    
    def clear(self) -> None:
        """Clear Pinecone index"""
        try:
            if self.index:
                self.index.delete(delete_all=True)
                logger.info("Cleared Pinecone index")
        except Exception as e:
            logger.error(f"Failed to clear Pinecone index: {str(e)}")

class VectorDBManager:
    """Manager class for vector database operations"""
    
    def __init__(self, use_pinecone: bool = False, pinecone_config: Optional[Dict[str, str]] = None):
        self.use_pinecone = use_pinecone
        self.db = None
        
        if use_pinecone and pinecone_config:
            if not PINECONE_AVAILABLE:
                logger.warning("Pinecone not available, falling back to FAISS")
                self.use_pinecone = False
                self.db = FAISSVectorDB()
            else:
                try:
                    self.db = PineconeVectorDB(
                        api_key=pinecone_config["api_key"],
                        environment=pinecone_config["environment"],
                        index_name=pinecone_config["index_name"]
                    )
                except Exception as e:
                    logger.warning(f"Failed to initialize Pinecone, falling back to FAISS: {str(e)}")
                    self.use_pinecone = False
                    self.db = FAISSVectorDB()
        else:
            self.db = FAISSVectorDB()
        
        logger.info(f"Initialized VectorDBManager with {'Pinecone' if self.use_pinecone else 'FAISS'}")
    
    def initialize(self, dimension: int) -> None:
        """Initialize the vector database"""
        self.db.initialize(dimension)
    
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """Add document chunks with embeddings to the database"""
        try:
            vectors = np.array([chunk["embedding"] for chunk in chunks])
            metadata = [{k: v for k, v in chunk.items() if k != "embedding"} for chunk in chunks]
            
            self.db.add_vectors(vectors, metadata)
            logger.info(f"Added {len(chunks)} chunks to vector database")
            
        except Exception as e:
            logger.error(f"Failed to add chunks to vector database: {str(e)}")
            raise Exception(f"Failed to add chunks to vector database: {str(e)}")
    
    def search_similar_chunks(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar chunks"""
        return self.db.search(query_embedding, top_k)
    
    def clear(self) -> None:
        """Clear the vector database"""
        self.db.clear()
