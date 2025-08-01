# LLM-Powered Intelligent Query-Retrieval System

An intelligent document processing and query answering system built with FastAPI, vector databases (FAISS/Pinecone), and Google Gemini AI for semantic search and natural language processing.

## Features

- **PDF Document Processing**: Download and parse PDF documents from URLs
- **Intelligent Chunking**: Smart text segmentation with overlap for context preservation
- **Vector Embeddings**: Convert text to semantic embeddings using sentence transformers
- **Dual Vector DB Support**: FAISS (local) and Pinecone (cloud) vector database options
- **LLM-Powered Analysis**: Query understanding and answer generation using Google Gemini
- **Semantic Search**: Retrieve relevant document sections based on query intent
- **Explainable Answers**: Structured responses with document citations
- **RESTful API**: FastAPI-based API with authentication and comprehensive documentation
- **Webhook Support**: No-authentication endpoint for automated testing

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PDF Input     │───▶│  PDF Processor   │───▶│  Text Chunks    │
│   (URL)         │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  LLM Response   │◀───│  LLM Processor   │◀───│  Embedding Gen  │
│  (Final Answer) │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                ▲                       │
                                │                       ▼
                        ┌──────────────────┐    ┌─────────────────┐
                        │  Retrieved       │◀───│  Vector Database│
                        │  Content         │    │  (FAISS/Pinecone)│
                        └──────────────────┘    └─────────────────┘
                                ▲                       ▲
                                │                       │
                        ┌──────────────────┐           │
                        │  Semantic Search │───────────┘
                        │                  │
                        └──────────────────┘
```

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd hackrx

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` file:

```env
# Required: Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Pinecone Configuration (FAISS used as fallback)
USE_PINECONE=false
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=hackrx384

# API Configuration
API_TOKEN=your_secure_api_token_here
```

### 3. Run the Application

```bash
# Start the FastAPI server
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API Base**: http://localhost:8000/api/v1
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Usage

### Authentication

All endpoints require Bearer token authentication (except webhook):

```bash
Authorization: Bearer your_secure_api_token_here
```

### Main Endpoint

**POST** `/api/v1/hackrx/run`

Process a PDF document and answer questions about its content.

### Webhook Endpoint (No Authentication)

**POST** `/api/v1/webhook/test`

Same functionality as main endpoint but without authentication - perfect for automated testing.

#### Request Body

```json
{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?"
    ]
}
```

#### Response

```json
{
    "answers": [
        "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
        "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
        "No, this policy generally excludes maternity expenses except for ectopic pregnancy. Expenses related to childbirth and miscarriage are excluded."
    ]
}
```

### Other Endpoints

- **GET** `/api/v1/health` - Health check
- **GET** `/api/v1/status` - Detailed system status

## Configuration Options

### Vector Database

**FAISS (Default)**
- No additional setup required
- Runs locally in memory
- Good for development and testing

**Pinecone (Optional)**
- Requires Pinecone account and API key
- Scalable cloud vector database
- Better for production workloads

```env
USE_PINECONE=true
PINECONE_API_KEY=your_api_key
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=hackrx-policy-index
```

### LLM Configuration

```env
LLM_MODEL=gemini-2.0-flash
LLM_PROVIDER=gemini
MAX_TOKENS=1000
TEMPERATURE=0.4
```

### Document Processing

```env
CHUNK_SIZE=500        # Size of text chunks
CHUNK_OVERLAP=50      # Overlap between chunks
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Sentence transformer model
```

## Project Structure

```
hackrx/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
├── .env                   # Environment configuration (create from example)
├── README.md              # This file
├── sample docs/           # Sample PDF documents
└── src/
    ├── __init__.py
    ├── config/            # Configuration management
    │   ├── __init__.py
    │   └── settings.py
    ├── api/               # FastAPI routes and models
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── endpoints.py
    │   └── models.py
    ├── components/        # Core system components
    │   ├── __init__.py
    │   ├── pdf_processor.py
    │   ├── embedding_generator.py
    │   ├── vector_db_manager.py
    │   ├── llm_query_processor.py
    │   └── query_retrieval_system.py
    └── utils/             # Utility functions
        ├── __init__.py
        ├── helpers.py
        └── logging_config.py
```

## Component Details

### PDF Processor (`pdf_processor.py`)
- Downloads PDFs from URLs
- Extracts text with page information
- Creates overlapping chunks for context preservation
- Handles various PDF formats using PyMuPDF

### Embedding Generator (`embedding_generator.py`)
- Converts text to vector embeddings
- Uses sentence-transformers library
- Supports multiple embedding models
- Batch processing for efficiency

### Vector Database Manager (`vector_db_manager.py`)
- Abstraction layer for vector databases
- FAISS implementation for local development
- Pinecone implementation for cloud deployment
- Automatic fallback mechanisms

### LLM Query Processor (`llm_query_processor.py`)
- Parses natural language queries
- Enhances queries for better retrieval
- Evaluates retrieved content using LLM
- Generates explainable answers with citations

### Query Retrieval System (`query_retrieval_system.py`)
- Orchestrates the complete pipeline
- Manages component interactions
- Handles error recovery and logging
- Provides system status information

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Quality

```bash
# Install development dependencies
pip install black isort flake8

# Format code
black .
isort .

# Check code quality
flake8 .
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Production Considerations

### Security
- Use secure API tokens
- Implement rate limiting
- Configure CORS appropriately
- Use HTTPS in production
- Secure environment variable management

### Performance
- Use Pinecone for large-scale deployments
- Implement caching for frequently accessed documents
- Consider async processing for large documents
- Monitor memory usage with large embedding models

### Monitoring
- Set up proper logging
- Monitor API response times
- Track embedding generation performance
- Monitor vector database operations

### Scaling
- Use load balancers for multiple instances
- Consider GPU acceleration for embedding generation
- Implement document preprocessing pipelines
- Use message queues for batch processing

## Troubleshooting

### Common Issues

1. **Google Gemini API Key Issues**
   ```
   Error: Gemini API key not configured
   Solution: Set GEMINI_API_KEY in .env file
   ```

2. **PDF Download Failures**
   ```
   Error: Failed to download PDF
   Solution: Check URL accessibility and network connectivity
   ```

3. **Memory Issues with Large Documents**
   ```
   Error: Out of memory during embedding generation
   Solution: Reduce chunk_size or process documents in batches
   ```

4. **Pinecone Connection Issues**
   ```
   Error: Failed to initialize Pinecone
   Solution: Check API key and environment settings, system will fallback to FAISS
   ```

### Logging

The system provides comprehensive logging. Check logs for:
- Document processing status
- Embedding generation progress
- Vector database operations
- LLM API calls and responses

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Check system status at `/api/v1/status`
4. Enable debug logging for detailed information
