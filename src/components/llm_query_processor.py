"""
LLM Query Processor for parsing queries and evaluating retrieved content using Google Gemini
"""
import logging
from typing import List, Dict, Any, Optional
import json
import re

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class LLMQueryProcessor:
    """Handles LLM-based query processing and content evaluation using Google Gemini"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", max_tokens: int = 1000, temperature: float = 0.4):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        if not GEMINI_AVAILABLE:
            raise Exception("Google Gemini library not available. Install with: pip install google-generativeai")
        
        # Initialize Gemini client
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(model)
        
        logger.info(f"Initialized LLM Query Processor with Gemini model {model}")
    
    def parse_query(self, query: str, document_context: str = "") -> Dict[str, Any]:
        """Parse natural language query to extract intent and key entities"""
        try:
            prompt = f"""
You are an expert at analyzing natural language queries about policy documents and insurance contracts.

Given the following query, extract:
1. The main intent/question type
2. Key entities mentioned (medical procedures, conditions, benefits, etc.)
3. Keywords that would be useful for retrieval
4. Any specific clauses or sections that might be relevant

Query: "{query}"

Document context (first 500 chars): "{document_context[:500]}..."

Respond in JSON format:
{{
    "intent": "coverage_inquiry|waiting_period|benefits|exclusions|definitions|other",
    "key_entities": ["entity1", "entity2"],
    "keywords": ["keyword1", "keyword2"],
    "query_type": "yes_no|definition|specific_value|list|explanation",
    "refined_query": "A more specific search-friendly version of the query"
}}
"""
            
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=self.temperature,
                )
            )
            
            content = response.text.strip()
            
            # Try to parse JSON response
            try:
                parsed_query = json.loads(content)
            except json.JSONDecodeError:
                # Fallback to basic parsing
                parsed_query = {
                    "intent": "other",
                    "key_entities": self._extract_entities_fallback(query),
                    "keywords": query.lower().split(),
                    "query_type": "explanation",
                    "refined_query": query
                }
            
            logger.info(f"Parsed query: {parsed_query['intent']}")
            return parsed_query
            
        except Exception as e:
            logger.error(f"Failed to parse query with LLM: {str(e)}")
            # Return fallback parsing
            return {
                "intent": "other",
                "key_entities": self._extract_entities_fallback(query),
                "keywords": query.lower().split(),
                "query_type": "explanation",
                "refined_query": query
            }
    
    def evaluate_retrieved_content(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Evaluate retrieved content and generate a comprehensive answer"""
        try:
            # Prepare context from retrieved chunks
            context_parts = []
            for i, chunk in enumerate(retrieved_chunks[:5]):  # Use top 5 chunks
                content = chunk.get("content", "")
                page_num = chunk.get("page_number", "unknown")
                chunk_id = chunk.get("chunk_id", f"chunk_{i}")
                
                context_parts.append(f"[Chunk {chunk_id}, Page {page_num}]: {content}")
            
            context = "\n\n".join(context_parts)
            
            prompt = f"""
You are an expert insurance policy analyst. Based on the retrieved document content, provide a comprehensive and accurate answer to the user's question.

IMPORTANT INSTRUCTIONS:
1. Answer the question directly and clearly
2. If the information is available, provide specific details and conditions
3. If the information is not explicitly stated, say so clearly
4. Include citations in the format <Page X> where X is the page number
5. If there are conditions or limitations, explain them clearly
6. Be precise with numbers, timeframes, and percentages when mentioned

Question: "{query}"

Retrieved Content:
{context}

Provide a clear, factual answer based solely on the retrieved content. Include page citations where appropriate.
"""
            
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )
            
            answer = response.text.strip()
            logger.info("Generated answer using LLM evaluation")
            return answer
            
        except Exception as e:
            logger.error(f"Failed to evaluate content with LLM: {str(e)}")
            # Return fallback answer
            return self._generate_fallback_answer(query, retrieved_chunks)
    
    def _extract_entities_fallback(self, query: str) -> List[str]:
        """Fallback entity extraction using simple patterns"""
        entities = []
        
        # Common medical/insurance terms
        medical_terms = [
            "surgery", "treatment", "procedure", "condition", "disease", "illness",
            "hospitalization", "medication", "therapy", "diagnosis", "consultation"
        ]
        
        insurance_terms = [
            "coverage", "benefit", "premium", "deductible", "copay", "claim",
            "policy", "waiting period", "grace period", "exclusion", "limit"
        ]
        
        query_lower = query.lower()
        
        for term in medical_terms + insurance_terms:
            if term in query_lower:
                entities.append(term)
        
        # Extract potential procedure names (capitalized words)
        words = query.split()
        for word in words:
            if word[0].isupper() and len(word) > 3:
                entities.append(word.lower())
        
        return list(set(entities))
    
    def _generate_fallback_answer(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Generate a basic answer when LLM evaluation fails"""
        if not retrieved_chunks:
            return "The provided document does not contain information relevant to your query."
        
        # Extract the most relevant content
        best_chunk = retrieved_chunks[0]
        content = best_chunk.get("content", "")
        page_num = best_chunk.get("page_number", "unknown")
        
        return f"Based on the document content <Page {page_num}>, the relevant information found is: {content[:300]}..."
    
    def enhance_query_for_search(self, original_query: str, parsed_query: Dict[str, Any]) -> str:
        """Enhance the original query for better vector search"""
        try:
            # Combine original query with extracted keywords and entities
            enhanced_parts = [original_query]
            
            if parsed_query.get("key_entities"):
                enhanced_parts.extend(parsed_query["key_entities"])
            
            if parsed_query.get("refined_query") and parsed_query["refined_query"] != original_query:
                enhanced_parts.append(parsed_query["refined_query"])
            
            # Join with spaces and remove duplicates
            enhanced_query = " ".join(enhanced_parts)
            
            return enhanced_query
            
        except Exception as e:
            logger.error(f"Failed to enhance query: {str(e)}")
            return original_query
