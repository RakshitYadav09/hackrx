"""
Main Query Retrieval System orchestrating all components
"""
import logging
from typing import List, Dict, Any, Optional
import asyncio
from .pdf_processor import PDFProcessor
from .embedding_generator import EmbeddingGenerator
from .vector_db_manager import VectorDBManager
from .llm_query_processor import LLMQueryProcessor

logger = logging.getLogger(__name__)

class QueryRetrievalSystem:
    """Main system orchestrating document processing and query answering"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the query retrieval system with configuration"""
        self.config = config
        
        # Initialize components
        self.pdf_processor = PDFProcessor(
            chunk_size=config.get("chunk_size", 500),
            chunk_overlap=config.get("chunk_overlap", 50)
        )
        
        self.embedding_generator = EmbeddingGenerator(
            model_name=config.get("embedding_model", "all-MiniLM-L6-v2")
        )
        
        # Vector DB configuration
        vector_db_config = None
        if config.get("use_pinecone", False):
            vector_db_config = {
                "api_key": config.get("pinecone_api_key"),
                "environment": config.get("pinecone_environment"),
                "index_name": config.get("pinecone_index_name", "hackrx-policy-index")
            }
        
        self.vector_db = VectorDBManager(
            use_pinecone=config.get("use_pinecone", False),
            pinecone_config=vector_db_config
        )
        
        self.llm_processor = LLMQueryProcessor(
            api_key=config.get("gemini_api_key"),
            model=config.get("llm_model", "gemini-1.5-flash"),
            max_tokens=config.get("max_tokens", 1000),
            temperature=config.get("temperature", 0.4)
        )
        
        logger.info("Initialized Query Retrieval System")
    
    async def process_document_and_questions(self, document_url: str, questions: List[str]) -> Dict[str, Any]:
        """Process a document and answer multiple questions"""
        try:
            logger.info(f"Processing document: {document_url}")
            
            # Step 1: Process PDF document
            chunks = await self.pdf_processor.process_document(document_url)
            
            if not chunks:
                raise Exception("No content extracted from document")
            
            # Step 2: Generate embeddings for chunks
            chunks_with_embeddings = self.embedding_generator.process_chunks_for_embedding(chunks)
            
            # Step 3: Initialize and populate vector database
            embedding_dimension = self.embedding_generator.get_embedding_dimension()
            self.vector_db.initialize(embedding_dimension)
            self.vector_db.add_chunks(chunks_with_embeddings)
            
            # Step 4: Process each question
            answers = []
            document_context = " ".join([chunk["content"] for chunk in chunks[:3]])  # First 3 chunks for context
            
            for question in questions:
                logger.info(f"Processing question: {question[:50]}...")
                answer = await self._answer_single_question(question, document_context)
                answers.append(answer)
            
            # Clear vector database for memory efficiency
            self.vector_db.clear()
            
            return {"answers": answers}
            
        except Exception as e:
            logger.error(f"Failed to process document and questions: {str(e)}")
            raise Exception(f"Document processing failed: {str(e)}")
    
    async def _answer_single_question(self, question: str, document_context: str) -> str:
        """Answer a single question using the complete pipeline"""
        try:
            # Step 1: Parse the query using LLM
            parsed_query = self.llm_processor.parse_query(question, document_context)
            
            # Step 2: Enhance query for better search
            enhanced_query = self.llm_processor.enhance_query_for_search(question, parsed_query)
            
            # Step 3: Generate query embedding
            query_embedding = self.embedding_generator.generate_query_embedding(enhanced_query)
            
            # Step 4: Retrieve similar chunks
            similar_chunks = self.vector_db.search_similar_chunks(query_embedding, top_k=10)
            
            if not similar_chunks:
                return "The provided document does not contain information relevant to your query."
            
            # Step 5: Extract chunk data (without similarity scores for LLM processing)
            retrieved_chunks = [chunk_data for chunk_data, score in similar_chunks]
            
            # Step 6: Use LLM to evaluate content and generate answer
            answer = self.llm_processor.evaluate_retrieved_content(question, retrieved_chunks)
            
            return answer
            
        except Exception as e:
            logger.error(f"Failed to answer question: {str(e)}")
            return f"An error occurred while processing your question: {str(e)}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "pdf_processor": "ready",
            "embedding_generator": {
                "model": self.embedding_generator.model_name,
                "dimension": self.embedding_generator.get_embedding_dimension()
            },
            "vector_db": {
                "type": "Pinecone" if self.vector_db.use_pinecone else "FAISS",
                "status": "ready"
            },
            "llm_processor": {
                "model": self.llm_processor.model,
                "status": "ready"
            }
        }
