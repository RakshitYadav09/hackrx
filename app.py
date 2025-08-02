"""
Enhanced HackRX Document Query System - Improved for 50%+ Accuracy
Optimized for handling diverse document types with better accuracy
"""
from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import google.generativeai as genai
import requests
import PyPDF2
import io
import os
import re
from typing import List, Dict, Any
import time
import logging
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_TOKEN = os.getenv("API_TOKEN", "1fcad8c4ef8f698546d9a985893a9bfa5c60c562930511aa5c5e2ac8366de6fc")

if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY is required")

genai.configure(api_key=GEMINI_API_KEY)

# FastAPI app
app = FastAPI(
    title="HackRX Enhanced Document Query System",
    description="High-accuracy document processing optimized for diverse document types",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return {"authenticated": True}

# Request/Response models
class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]
    success: bool
    processing_time: float
    timestamp: float
    confidence_scores: List[float] = []

# Enhanced Document Processing Functions
def download_pdf_with_retry(url: str, max_retries: int = 3) -> bytes:
    """Download PDF with retry logic and support for very large documents"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Downloading PDF document with enhanced retry logic (attempt {attempt + 1})...")
            
            # Use headers to handle potential issues
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/pdf,application/octet-stream,*/*'
            }
            
            # Use streaming for large files with longer timeout
            response = requests.get(url, timeout=180, stream=True, headers=headers)  # Increased timeout
            response.raise_for_status()
            
            content = b""
            downloaded_size = 0
            max_size = 200 * 1024 * 1024  # Increased to 200MB for very large documents
            
            for chunk in response.iter_content(chunk_size=16384):  # Larger chunks for efficiency
                if chunk:
                    content += chunk
                    downloaded_size += len(chunk)
                    
                    # Progress logging for large files
                    if downloaded_size % (10 * 1024 * 1024) == 0:  # Every 10MB
                        logger.info(f"Downloaded {downloaded_size / (1024*1024):.1f}MB...")
                    
                    # Only limit if absolutely necessary to prevent memory issues
                    if downloaded_size > max_size:
                        logger.warning(f"Document very large ({downloaded_size / (1024*1024):.1f}MB), truncating to {max_size / (1024*1024):.1f}MB for processing...")
                        break
            
            if len(content) < 1000:  # Minimum viable PDF size
                raise ValueError("Downloaded content too small to be a valid PDF")
            
            logger.info(f"Successfully downloaded PDF ({len(content) / (1024*1024):.1f}MB)")
            return content
            
        except requests.exceptions.Timeout:
            logger.warning(f"Download timeout on attempt {attempt + 1}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Download request failed on attempt {attempt + 1}: {e}")
        except Exception as e:
            logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            
        if attempt < max_retries - 1:
            wait_time = 3 ** attempt  # Exponential backoff (3, 9, 27 seconds)
            logger.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to download PDF after {max_retries} attempts. The document may be too large or temporarily unavailable."
            )

def extract_text_from_pdf_enhanced(pdf_content: bytes) -> str:
    """Enhanced text extraction with robust handling for very large PDFs"""
    try:
        # First attempt with PyPDF2
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file, strict=False)  # Non-strict mode
            
            text = ""
            total_pages = len(pdf_reader.pages)
            max_pages = min(total_pages, 200)  # Increased to 200 pages for large documents
            
            logger.info(f"Processing PDF with {total_pages} pages, extracting from first {max_pages} pages")
            
            for i, page in enumerate(pdf_reader.pages[:max_pages]):
                try:
                    page_text = page.extract_text()
                    if page_text and len(page_text.strip()) > 10:
                        text += page_text + "\n"
                        
                    # Progress for very large documents
                    if (i + 1) % 20 == 0:
                        logger.info(f"Processed {i + 1}/{max_pages} pages...")
                        
                    # Increase content limit for comprehensive extraction
                    if len(text) > 100000:  # 100K characters - much more content
                        logger.info(f"Extracted comprehensive content from first {i+1} pages ({len(text)} characters)")
                        break
                        
                except Exception as page_error:
                    logger.warning(f"Error extracting page {i}: {page_error}")
                    continue
            
            if len(text.strip()) > 100:  # Ensure we got meaningful content
                text = clean_text(text)
                logger.info(f"Successfully extracted {len(text)} characters from PDF using PyPDF2")
                return text.strip()
                
        except Exception as pdf_error:
            logger.warning(f"PyPDF2 failed: {pdf_error}")
        
        # Fallback: Try alternative PDF processing with PyMuPDF
        try:
            import fitz  # PyMuPDF fallback
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            text = ""
            total_pages = doc.page_count
            max_pages = min(total_pages, 200)  # Process up to 200 pages
            
            logger.info(f"Fallback: Processing {total_pages} pages with PyMuPDF, extracting from first {max_pages} pages")
            
            for page_num in range(max_pages):
                try:
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    if page_text and len(page_text.strip()) > 10:
                        text += page_text + "\n"
                        
                    # Progress logging
                    if (page_num + 1) % 20 == 0:
                        logger.info(f"PyMuPDF processed {page_num + 1}/{max_pages} pages...")
                        
                    if len(text) > 100000:  # 100K characters
                        logger.info(f"PyMuPDF extracted comprehensive content from first {page_num+1} pages")
                        break
                except Exception as page_error:
                    logger.warning(f"PyMuPDF page {page_num} error: {page_error}")
                    continue
            
            doc.close()
            if len(text.strip()) > 100:
                text = clean_text(text)
                logger.info(f"Successfully extracted {len(text)} characters using PyMuPDF fallback")
                return text.strip()
                
        except ImportError:
            logger.warning("PyMuPDF not available for fallback")
        except Exception as fallback_error:
            logger.warning(f"PyMuPDF fallback failed: {fallback_error}")
        
        # Final attempt: Try to extract from first portion for very problematic PDFs
        if len(pdf_content) > 1000:
            try:
                # Try with first 50MB of the PDF
                partial_content = pdf_content[:min(len(pdf_content), 50 * 1024 * 1024)]
                pdf_file = io.BytesIO(partial_content)
                pdf_reader = PyPDF2.PdfReader(pdf_file, strict=False)
                
                text = ""
                max_pages = min(len(pdf_reader.pages), 50)  # Even more conservative
                
                logger.info(f"Last attempt: Processing partial PDF with {max_pages} pages")
                
                for i, page in enumerate(pdf_reader.pages[:max_pages]):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                        if len(text) > 50000:  # 50K characters minimum
                            break
                    except:
                        continue
                
                if len(text.strip()) > 100:
                    text = clean_text(text)
                    logger.info(f"Partial extraction successful: {len(text)} characters")
                    return text.strip()
                    
            except Exception as partial_error:
                logger.warning(f"Partial extraction failed: {partial_error}")
        
        # Last resort: return meaningful error message instead of crashing
        logger.error("All PDF extraction methods failed for this document")
        return "ERROR: Unable to extract text from this PDF document. The document may be corrupted, password-protected, or in an unsupported format. Please try with a different document."
        
    except Exception as e:
        logger.error(f"Critical error in PDF extraction: {e}")
        return "ERROR: Critical failure in PDF processing. Please contact support for assistance with this document type."

def clean_text(text: str) -> str:
    """Clean and normalize extracted text"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page numbers and common PDF artifacts
    text = re.sub(r'\n\d+\n', '\n', text)
    text = re.sub(r'\f', '\n', text)
    
    # Fix common OCR issues
    text = text.replace('fi', 'fi').replace('fl', 'fl')
    
    return text

def detect_document_type(text: str) -> str:
    """Detect document type based on content analysis"""
    text_lower = text.lower()
    
    # Insurance policy indicators
    insurance_keywords = ['policy', 'premium', 'insured', 'coverage', 'beneficiary', 'claim']
    insurance_score = sum(1 for keyword in insurance_keywords if keyword in text_lower)
    
    # Legal document indicators
    legal_keywords = ['constitution', 'article', 'section', 'law', 'court', 'legal']
    legal_score = sum(1 for keyword in legal_keywords if keyword in text_lower)
    
    # Scientific document indicators
    science_keywords = ['theorem', 'principle', 'mathematical', 'physics', 'equation', 'law of']
    science_score = sum(1 for keyword in science_keywords if keyword in text_lower)
    
    scores = {
        'insurance': insurance_score,
        'legal': legal_score,
        'scientific': science_score
    }
    
    return max(scores, key=scores.get)

def chunk_text_intelligently(text: str, doc_type: str, max_chunk_size: int = 4000) -> List[str]:
    """Intelligently chunk text based on document type"""
    
    if doc_type == 'legal':
        # Split by articles/sections for legal documents
        chunks = re.split(r'(?i)(article|section)\s+\d+', text)
    elif doc_type == 'insurance':
        # Split by policy sections
        chunks = re.split(r'(?i)(section|clause|part)\s+\d+', text)
    elif doc_type == 'scientific':
        # Split by chapters or major headings
        chunks = re.split(r'(?i)(chapter|book|proposition)\s+\d+', text)
    else:
        # Default paragraph-based chunking
        chunks = text.split('\n\n')
    
    # Ensure chunks don't exceed max size
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_chunk_size:
            final_chunks.append(chunk.strip())
        else:
            # Split large chunks further
            sub_chunks = [chunk[i:i+max_chunk_size] for i in range(0, len(chunk), max_chunk_size)]
            final_chunks.extend(sub_chunks)
    
    return [chunk for chunk in final_chunks if len(chunk.strip()) > 50]

def find_relevant_chunks(chunks: List[str], question: str, max_chunks: int = 5) -> List[str]:
    """Find most relevant chunks for a question using keyword matching"""
    question_lower = question.lower()
    question_words = set(re.findall(r'\b\w+\b', question_lower))
    
    chunk_scores = []
    for i, chunk in enumerate(chunks):
        chunk_lower = chunk.lower()
        chunk_words = set(re.findall(r'\b\w+\b', chunk_lower))
        
        # Calculate overlap score
        overlap = len(question_words.intersection(chunk_words))
        
        # Bonus for exact phrase matches
        for word in question_words:
            if len(word) > 3 and word in chunk_lower:
                overlap += 1
        
        chunk_scores.append((overlap, i, chunk))
    
    # Sort by score and return top chunks
    chunk_scores.sort(reverse=True, key=lambda x: x[0])
    return [chunk for _, _, chunk in chunk_scores[:max_chunks]]

def generate_enhanced_prompt(document_text: str, question: str, doc_type: str) -> str:
    """Generate enhanced prompts based on document type"""
    
    base_prompt = f"""
    You are an expert document analyst specializing in {doc_type} documents. 
    Analyze the following document and provide a comprehensive, accurate answer to the question.
    
    Document Content:
    {document_text}
    
    Question: {question}
    
    Instructions:
    """
    
    if doc_type == 'insurance':
        specific_instructions = """
        1. Look for specific amounts, percentages, terms, and conditions
        2. Identify policy benefits, exclusions, and waiting periods
        3. Quote exact figures when available (₹ amounts, percentages, time periods)
        4. Explain coverage details clearly
        5. If information is not explicitly stated, mention that clearly
        """
    elif doc_type == 'legal':
        specific_instructions = """
        1. Reference specific articles, sections, or clauses
        2. Explain legal principles and constitutional provisions
        3. Describe procedures and processes accurately
        4. Use proper legal terminology
        5. Structure the answer logically with clear points
        """
    elif doc_type == 'scientific':
        specific_instructions = """
        1. Explain scientific principles and laws clearly
        2. Include mathematical formulations if present
        3. Describe experimental methods and observations
        4. Use precise scientific terminology
        5. Connect concepts to broader scientific understanding
        """
    else:
        specific_instructions = """
        1. Provide detailed, accurate information from the document
        2. Include specific details, numbers, and facts
        3. Structure the answer clearly and logically
        4. Use professional language appropriate to the document type
        5. If information is not available, state that explicitly
        """
    
    return base_prompt + specific_instructions + "\n\nAnswer:"

def process_question_with_enhanced_gemini(document_text: str, question: str, doc_type: str) -> tuple[str, float]:
    """Process question using enhanced Gemini with confidence scoring and rate limiting"""
    try:
        # Add delay to prevent quota exhaustion
        time.sleep(2)  # 2 second delay between API calls
        
        model = genai.GenerativeModel('gemini-2.0-flash-lite')  # Using stable available model
        
        # Chunk the document intelligently
        chunks = chunk_text_intelligently(document_text, doc_type)
        relevant_chunks = find_relevant_chunks(chunks, question)
        
        # Use the most relevant chunks for context
        context_text = "\n\n".join(relevant_chunks[:3])  # Top 3 chunks
        
        # Generate enhanced prompt
        prompt = generate_enhanced_prompt(context_text, question, doc_type)
        
        # Configure generation with better parameters for quota efficiency
        generation_config = genai.types.GenerationConfig(
            temperature=0.2,  # Lower temperature for more focused answers
            top_p=0.8,
            top_k=40,
            max_output_tokens=1000,
        )
        
        response = model.generate_content(prompt, generation_config=generation_config)
        answer = response.text.strip()
        
        # Calculate confidence score based on answer quality
        confidence = calculate_confidence_score(answer, question, context_text)
        
        return answer, confidence
        
    except Exception as e:
        logger.error(f"Error processing with Gemini: {e}")
        return f"Unable to process question due to technical error: {str(e)}", 0.0

def calculate_confidence_score(answer: str, question: str, context: str) -> float:
    """Calculate confidence score for the answer"""
    if not answer or len(answer) < 20:
        return 0.0
    
    confidence = 0.0
    
    # Length factor (20%)
    if len(answer) > 50:
        confidence += 0.2
    
    # Specific information factor (30%)
    specific_indicators = ['₹', '%', 'section', 'article', 'clause', 'specifically', 'mentioned']
    specific_count = sum(1 for indicator in specific_indicators if indicator.lower() in answer.lower())
    confidence += min(specific_count / 5, 0.3)
    
    # Question relevance factor (30%)
    question_words = set(re.findall(r'\b\w+\b', question.lower()))
    answer_words = set(re.findall(r'\b\w+\b', answer.lower()))
    overlap = len(question_words.intersection(answer_words))
    confidence += min(overlap / len(question_words), 0.3)
    
    # Context utilization factor (20%)
    if context and any(phrase in answer.lower() for phrase in ['according to', 'document states', 'mentioned', 'specified']):
        confidence += 0.2
    
    return min(confidence, 1.0)

# Enhanced API Endpoints
@app.get("/")
async def root():
    return {
        "message": "HackRX Enhanced Document Query System",
        "status": "running",
        "version": "2.0.0",
        "optimizations": ["intelligent_chunking", "document_type_detection", "confidence_scoring"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "HackRX Enhanced Document Query System",
        "timestamp": time.time(),
        "capabilities": ["pdf_processing", "multi_document_types", "enhanced_accuracy"]
    }

@app.get("/api/v1/system-status")
async def system_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "status": "operational",
        "system_type": "enhanced_document_query_system",
        "model": "gemini-2.0-flash-lite",
        "capabilities": [
            "intelligent_pdf_processing",
            "document_type_detection", 
            "semantic_chunking",
            "confidence_scoring",
            "enhanced_accuracy"
        ],
        "optimizations": [
            "retry_logic",
            "memory_management",
            "context_aware_processing"
        ],
        "authenticated": True,
        "timestamp": time.time()
    }

@app.post("/api/v1/webhook/test", response_model=QueryResponse)
async def webhook_test(
    request: QueryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Enhanced webhook endpoint with improved accuracy and reliability"""
    start_time = time.time()
    
    try:
        logger.info(f"Processing enhanced request with {len(request.questions)} questions")
        
        # Validate input
        if not request.questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one question is required"
            )
        
        if len(request.questions) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 questions allowed per request"
            )
        
        # Download and process document with enhanced handling
        logger.info("Downloading PDF document with enhanced retry logic...")
        try:
            pdf_content = download_pdf_with_retry(request.documents)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download document: {str(e)}"
            )
        
        logger.info("Extracting text with enhanced PDF processing...")
        document_text = extract_text_from_pdf_enhanced(pdf_content)
        
        # Handle PDF extraction errors gracefully
        if not document_text or document_text.startswith("ERROR:"):
            if document_text and document_text.startswith("ERROR:"):
                error_msg = document_text
            else:
                error_msg = "No text could be extracted from the PDF document"
            
            # Instead of failing completely, return informative error responses
            answers = [f"Unable to process this document: {error_msg}. Please try with a different document or contact support for assistance with large/complex documents."] * len(request.questions)
            confidence_scores = [0.0] * len(request.questions)
            
            processing_time = time.time() - start_time
            return QueryResponse(
                answers=answers,
                success=False,
                processing_time=processing_time,
                timestamp=time.time(),
                confidence_scores=confidence_scores
            )
        
        # Detect document type for optimized processing
        doc_type = detect_document_type(document_text)
        logger.info(f"Detected document type: {doc_type}")
        
        # Process each question with enhanced AI and rate limiting
        answers = []
        confidence_scores = []
        
        for i, question in enumerate(request.questions):
            logger.info(f"Processing question {i+1}/{len(request.questions)} ({doc_type}): {question}")
            
            # Add delay between questions to prevent quota exhaustion
            if i > 0:  # Don't delay before first question
                delay_time = 3  # 3 seconds between questions
                logger.info(f"Rate limiting: waiting {delay_time}s before next question...")
                time.sleep(delay_time)
            
            answer, confidence = process_question_with_enhanced_gemini(document_text, question, doc_type)
            answers.append(answer)
            confidence_scores.append(confidence)
        
        processing_time = time.time() - start_time
        logger.info(f"Enhanced request processed successfully in {processing_time:.2f} seconds")
        
        return QueryResponse(
            answers=answers,
            success=True,
            processing_time=processing_time,
            timestamp=time.time(),
            confidence_scores=confidence_scores
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error processing enhanced request: {str(e)}")
        
        return QueryResponse(
            answers=[f"Unable to process question due to technical error: {str(e)}"],
            success=False,
            processing_time=processing_time,
            timestamp=time.time(),
            confidence_scores=[0.0]
        )

@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Alternative query endpoint with enhanced functionality"""
    return await webhook_test(request, current_user)

if __name__ == "__main__":
    print("🚀 Starting HackRX Enhanced Document Query System...")
    print("📍 Server: http://localhost:8001")
    print("📚 API Docs: http://localhost:8001/docs")
    print("🔑 Health Check: http://localhost:8001/health")
    print("✨ Features: Document Type Detection, Intelligent Chunking, Confidence Scoring")
    print("="*70)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
