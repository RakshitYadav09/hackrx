"""
Utility functions for the application
"""
import re
from typing import List, Dict, Any
import unicodedata

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove special characters that might interfere with processing
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/\\]', '', text)
    
    return text.strip()

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract potential keywords from text"""
    # Convert to lowercase and split
    words = text.lower().split()
    
    # Filter out common stop words and short words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
        'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    keywords = []
    for word in words:
        # Clean word
        word = re.sub(r'[^\w]', '', word)
        
        # Filter criteria
        if (len(word) >= min_length and 
            word not in stop_words and 
            not word.isdigit()):
            keywords.append(word)
    
    return list(set(keywords))

def format_citation(page_number: int, section: str = None) -> str:
    """Format citation for document reference"""
    if section:
        return f"<Page {page_number}, {section}>"
    return f"<Page {page_number}>"

def truncate_text(text: str, max_length: int = 1000, ellipsis: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    # Try to truncate at a sentence boundary
    truncated = text[:max_length]
    last_sentence = max(
        truncated.rfind('.'),
        truncated.rfind('!'),
        truncated.rfind('?')
    )
    
    if last_sentence > max_length // 2:  # If we found a reasonable sentence boundary
        return truncated[:last_sentence + 1] + ellipsis
    
    # Otherwise, truncate at word boundary
    last_space = truncated.rfind(' ')
    if last_space > max_length // 2:
        return truncated[:last_space] + ellipsis
    
    # Fallback: hard truncation
    return truncated + ellipsis

def validate_url(url: str) -> bool:
    """Validate if string is a proper URL"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary with nested key support"""
    try:
        keys = key.split('.')
        value = dictionary
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default
