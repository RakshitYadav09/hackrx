# Setup Guide for LLM-Powered Query Retrieval System

## Prerequisites

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - Ensure Python is added to your PATH

2. **OpenAI API Key**
   - Sign up at: https://platform.openai.com/
   - Create an API key in your account settings
   - You'll need this for LLM functionality

3. **Optional: Pinecone Account**
   - Sign up at: https://www.pinecone.io/
   - Create an index for vector storage
   - Get your API key and environment details

## Installation Steps

### Step 1: Environment Setup

```bash
# Navigate to the project directory
cd c:\code\hackrx

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration

1. **Copy environment template:**
   ```bash
   copy .env.example .env
   ```

2. **Edit .env file with your API keys:**
   ```env
   # Required: OpenAI API Key
   OPENAI_API_KEY=sk-your-openai-api-key-here
   
   # Optional: Pinecone Configuration
   USE_PINECONE=false
   PINECONE_API_KEY=your-pinecone-api-key
   PINECONE_ENVIRONMENT=your-pinecone-environment
   
   # API Token (already configured)
   API_TOKEN=1fcad8c4ef8f698546d9a985893a9bfa5c60c562930511aa5c5e2ac8366de6fc
   ```

### Step 3: Test Installation

```bash
# Test the system
python test_system.py
```

If successful, you should see:
- System initialization
- Component status
- Sample document processing
- Generated answers

### Step 4: Start the Application

```bash
# Start the FastAPI server
python main.py
```

Or use the Windows batch script:
```bash
start.bat
```

## Verification

1. **Check API Health:**
   - Open: http://localhost:8000/api/v1/health
   - Should return status "healthy"

2. **Access Documentation:**
   - Open: http://localhost:8000/docs
   - Interactive API documentation

3. **Test API Endpoint:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
   -H "Authorization: Bearer 1fcad8c4ef8f698546d9a985893a9bfa5c60c562930511aa5c5e2ac8366de6fc" \
   -H "Content-Type: application/json" \
   -d '{
     "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
     "questions": ["What is the grace period for premium payment?"]
   }'
   ```

## Troubleshooting

### Common Issues

1. **"OpenAI API key not configured"**
   - Solution: Add your OpenAI API key to the .env file

2. **"Module not found" errors**
   - Solution: Ensure virtual environment is activated and dependencies are installed
   - Run: `pip install -r requirements.txt`

3. **"Failed to download PDF"**
   - Solution: Check internet connectivity and PDF URL accessibility

4. **Memory issues with large documents**
   - Solution: Reduce CHUNK_SIZE in .env file (e.g., from 500 to 300)

5. **"Pinecone connection failed"**
   - Solution: Set USE_PINECONE=false to use FAISS instead

### Performance Optimization

1. **For faster processing:**
   - Use `gpt-3.5-turbo` instead of `gpt-4-turbo-preview`
   - Reduce MAX_TOKENS to 1000
   - Use smaller embedding model

2. **For better accuracy:**
   - Use `gpt-4-turbo-preview`
   - Increase CHUNK_OVERLAP to 100
   - Use larger embedding model like `all-mpnet-base-v2`

## Next Steps

1. **Test with your own documents:**
   - Replace the document URL with your PDF
   - Adjust questions based on your document content

2. **Customize for your use case:**
   - Modify chunk size and overlap
   - Adjust LLM temperature for creativity vs consistency
   - Add custom preprocessing for specific document types

3. **Deploy to production:**
   - Set up proper environment variables
   - Configure HTTPS
   - Implement rate limiting
   - Set up monitoring and logging

4. **Scale the system:**
   - Use Pinecone for larger document collections
   - Implement document caching
   - Add batch processing capabilities

## Support

- **Documentation:** http://localhost:8000/docs
- **System Status:** http://localhost:8000/api/v1/status
- **Logs:** Check console output for detailed information
