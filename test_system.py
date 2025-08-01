"""
Test script for the Query Retrieval System
"""
import asyncio
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.components import QueryRetrievalSystem
from src.config import settings

async def test_system():
    """Test the query retrieval system with sample data"""
    print("Testing LLM-Powered Query Retrieval System")
    print("=" * 50)
    
    # Configuration
    config = {
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "embedding_model": settings.embedding_model,
        "use_pinecone": settings.use_pinecone,  # Use the setting from .env
        "pinecone_api_key": settings.pinecone_api_key,
        "pinecone_environment": settings.pinecone_environment,
        "pinecone_index_name": settings.pinecone_index_name,
        "gemini_api_key": settings.gemini_api_key,
        "llm_model": settings.llm_model,
        "max_tokens": settings.max_tokens,
        "temperature": settings.temperature
    }
    
    try:
        # Initialize system
        print("1. Initializing system...")
        system = QueryRetrievalSystem(config)
        
        # Check system status
        print("2. Checking system status...")
        status = system.get_system_status()
        print(f"   Status: {json.dumps(status, indent=2)}")
        
        # Test document URL and questions
        document_url = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
        
        test_questions = [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?"
        ]
        
        print("3. Processing document and questions...")
        print(f"   Document: {document_url[:100]}...")
        print(f"   Questions: {len(test_questions)}")
        
        # Process questions
        result = await system.process_document_and_questions(document_url, test_questions)
        
        print("4. Results:")
        for i, answer in enumerate(result["answers"]):
            print(f"   Q{i+1}: {test_questions[i]}")
            print(f"   A{i+1}: {answer}")
            print()
        
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if Gemini API key is configured
    if not settings.gemini_api_key:
        print("❌ Gemini API key not configured. Please set GEMINI_API_KEY in .env file")
        sys.exit(1)
    
    # Run test
    asyncio.run(test_system())
