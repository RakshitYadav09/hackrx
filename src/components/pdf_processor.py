"""
PDF Processor Component for extracting and chunking text from PDF documents
"""
import logging
import re
from typing import List, Dict, Any
import fitz  # PyMuPDF
import requests
from io import BytesIO

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF parsing and text extraction"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    async def download_pdf(self, url: str) -> bytes:
        """Download PDF from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to download PDF from {url}: {str(e)}")
            raise Exception(f"Failed to download PDF: {str(e)}")
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> List[Dict[str, Any]]:
        """Extract text from PDF with page information"""
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            pages_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # Clean up the text
                text = self._clean_text(text)
                
                if text.strip():  # Only add non-empty pages
                    pages_content.append({
                        "page_number": page_num + 1,
                        "content": text,
                        "char_count": len(text)
                    })
            
            doc.close()
            logger.info(f"Extracted text from {len(pages_content)} pages")
            return pages_content
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove page headers/footers that might be repetitive
        # This is a basic implementation - can be enhanced based on document patterns
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:  # Ignore very short lines that might be artifacts
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def create_chunks(self, pages_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create overlapping chunks from the extracted text"""
        chunks = []
        chunk_id = 0
        
        for page_data in pages_content:
            page_num = page_data["page_number"]
            text = page_data["content"]
            
            # Split by paragraphs first
            paragraphs = text.split('\n\n')
            
            current_chunk = ""
            current_chunk_start = 0
            
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                # If adding this paragraph would exceed chunk size, finalize current chunk
                if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                    chunks.append({
                        "chunk_id": f"chunk_{chunk_id}",
                        "content": current_chunk.strip(),
                        "page_number": page_num,
                        "char_start": current_chunk_start,
                        "char_end": current_chunk_start + len(current_chunk)
                    })
                    chunk_id += 1
                    
                    # Start new chunk with overlap
                    overlap_text = self._get_overlap_text(current_chunk, self.chunk_overlap)
                    current_chunk = overlap_text + "\n\n" + para if overlap_text else para
                    current_chunk_start = current_chunk_start + len(current_chunk) - len(overlap_text) if overlap_text else current_chunk_start + len(current_chunk)
                else:
                    # Add paragraph to current chunk
                    if current_chunk:
                        current_chunk += "\n\n" + para
                    else:
                        current_chunk = para
            
            # Add the last chunk if it has content
            if current_chunk.strip():
                chunks.append({
                    "chunk_id": f"chunk_{chunk_id}",
                    "content": current_chunk.strip(),
                    "page_number": page_num,
                    "char_start": current_chunk_start,
                    "char_end": current_chunk_start + len(current_chunk)
                })
                chunk_id += 1
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """Get overlap text from the end of current chunk"""
        if len(text) <= overlap_size:
            return text
        
        # Try to find a good breaking point (end of sentence or paragraph)
        overlap_text = text[-overlap_size:]
        
        # Find the last complete sentence in the overlap
        sentence_end = max(
            overlap_text.rfind('.'),
            overlap_text.rfind('!'),
            overlap_text.rfind('?')
        )
        
        if sentence_end > overlap_size // 2:  # If we found a sentence end in reasonable position
            return overlap_text[sentence_end + 1:].strip()
        
        return overlap_text
    
    async def process_document(self, pdf_url: str) -> List[Dict[str, Any]]:
        """Complete document processing pipeline"""
        try:
            # Download PDF
            pdf_content = await self.download_pdf(pdf_url)
            
            # Extract text
            pages_content = self.extract_text_from_pdf(pdf_content)
            
            # Create chunks
            chunks = self.create_chunks(pages_content)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            raise
