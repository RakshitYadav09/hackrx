# HackRX Document Query System

A FastAPI-based intelligent document processing system that analyzes PDF documents and answers questions with high accuracy. The system uses Google's Gemini AI for natural language processing and supports large documents up to 200MB.

## Features

- 🤖 **AI-Powered Analysis**: Uses Google Gemini 1.5 Flash for intelligent document analysis
- 📄 **Large Document Support**: Handles PDFs up to 200MB and 200+ pages
- 🎯 **Document Type Detection**: Automatically detects insurance, legal, and scientific documents
- ⚡ **Rate Limiting**: Built-in rate limiting to prevent API quota exhaustion
- 🔒 **Secure API**: Token-based authentication for secure access
- 📊 **Confidence Scoring**: Provides confidence scores for each answer
- 🏥 **Health Monitoring**: Built-in health check endpoints

## Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API Key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/RakshitYadav09/hackrx.git
   cd hackrx
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Required: Google Gemini API Key
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Optional: API Authentication Token
   API_TOKEN=your_custom_api_token_here
   ```

4. **Start the server**
   ```bash
   python app.py
   ```

   The server will start on `http://localhost:8001`

5. **Test the system**
   ```bash
   python test_system.py
   ```

## API Usage

### Health Check
```bash
GET http://localhost:8001/health
```

### Process Document
```bash
POST http://localhost:8001/api/v1/webhook/test
Content-Type: application/json
Authorization: Bearer your_api_token

{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "What is the main topic of this document?",
    "What are the key findings?"
  ]
}
```

### Response Format
```json
{
  "answers": [
    "The main topic is...",
    "The key findings are..."
  ],
  "success": true,
  "processing_time": 5.23,
  "timestamp": 1754153966.965594,
  "confidence_scores": [0.85, 0.78]
}
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | - | ✅ |
| `API_TOKEN` | Authentication token | auto-generated | ❌ |

### Rate Limiting

The system includes built-in rate limiting:
- 2-second delay between API calls
- 3-second delay between questions
- Exponential backoff on retries

## Supported Document Types

- **Insurance Policies**: Automatically detects and optimizes for insurance documents
- **Legal Documents**: Enhanced processing for contracts, constitutions, and legal texts
- **Scientific Papers**: Optimized for research papers and technical documents
- **General Documents**: Works with any PDF document

## API Endpoints

### GET `/health`
Returns system health status and version information.

### POST `/api/v1/webhook/test`
Main endpoint for document processing and question answering.

**Headers:**
- `Authorization: Bearer {your_token}`
- `Content-Type: application/json`

**Body:**
- `documents` (string): URL to the PDF document
- `questions` (array): List of questions to ask about the document

## Testing

Run the test suite to verify everything is working:

```bash
python test_system.py
```

The test will check:
- Server health
- Document processing
- API responses
- Error handling

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment

1. **Using Docker** (recommended)
   ```bash
   # Build image
   docker build -t hackrx-system .
   
   # Run container
   docker run -p 8001:8001 --env-file .env hackrx-system
   ```

2. **Using a reverse proxy** (Nginx/Apache)
   Configure your web server to proxy requests to `localhost:8001`

3. **Using a cloud service**
   Deploy to services like AWS, Google Cloud, or Azure

### Environment Setup for Production

Create a production `.env` file:
```env
GEMINI_API_KEY=your_production_api_key
API_TOKEN=your_secure_production_token
```

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Ensure you have a `.env` file with a valid API key
   - Check that the API key has sufficient quota

2. **"429 You exceeded your current quota"**
   - Check your Google AI Studio quota
   - Wait for quota reset or upgrade your plan

3. **PDF processing errors**
   - Ensure the PDF URL is publicly accessible
   - Check that the file size is under 200MB

4. **Server won't start**
   - Check if port 8001 is already in use
   - Verify all dependencies are installed

### Getting Help

- Check the logs for detailed error messages
- Run `python test_system.py` to diagnose issues
- Ensure your `.env` file is properly configured

## Project Structure

```
hackrx/
├── app.py              # Main FastAPI application
├── test_system.py      # Test suite
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Changelog

### Version 2.0.0
- Enhanced document type detection
- Improved rate limiting
- Large document support (200MB)
- Better error handling
- Comprehensive test suite
