"""
Webhook Test Script for External Testing

This script tests the webhook endpoint without authentication.
Perfect for automated submission systems and external validators.
"""
import requests
import json
import sys
import argparse
from typing import List, Dict

def test_webhook(api_base_url: str, document_url: str, questions: List[str], verbose: bool = True) -> Dict:
    """
    Test the webhook endpoint
    
    Args:
        api_base_url (str): Base URL of the API
        document_url (str): URL to the PDF document
        questions (List[str]): List of questions to ask
        verbose (bool): Whether to print detailed output
    
    Returns:
        dict: API response or error information
    """
    
    if verbose:
        print("🔗 Testing Webhook Endpoint")
        print("=" * 60)
        print(f"📄 Document: {document_url}")
        print(f"❓ Questions: {len(questions)}")
        print("-" * 60)
    
    # Prepare the request (no authentication needed for webhook)
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "documents": document_url,
        "questions": questions
    }
    
    try:
        if verbose:
            print("🚀 Sending webhook request...")
        
        # Make the webhook API call
        response = requests.post(
            f"{api_base_url}/api/v1/webhook/test",
            headers=headers,
            json=payload,
            timeout=300  # 5 minutes timeout for large documents
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if verbose:
                print("✅ Webhook request successful!")
                print("\n📋 Results:")
                print("=" * 60)
                
                for i, (question, answer) in enumerate(zip(questions, result["answers"]), 1):
                    print(f"\n🔍 Question {i}:")
                    print(f"   {question}")
                    print(f"\n💡 Answer {i}:")
                    print(f"   {answer}")
                    print("-" * 40)
                
                # Webhook-specific metadata
                if result.get("webhook"):
                    print(f"\n🔗 Webhook ID: {result.get('request_id', 'N/A')}")
                    print(f"⏱️  Processing time: {result.get('processing_time', 'N/A')} seconds")
                    print(f"📊 Timestamp: {result.get('timestamp', 'N/A')}")
            
            return {
                "success": True,
                "data": result
            }
        
        else:
            error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            if verbose:
                print(f"❌ Webhook request failed with status {response.status_code}")
                print(f"Error: {error_detail}")
            
            return {
                "success": False,
                "status_code": response.status_code,
                "error": error_detail
            }
    
    except requests.exceptions.Timeout:
        if verbose:
            print("⏰ Webhook request timed out (5 minutes). Document might be too large.")
        return {"success": False, "error": "Request timeout"}
    
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"🔌 Connection error: {str(e)}")
        return {"success": False, "error": f"Connection error: {str(e)}"}
    
    except Exception as e:
        if verbose:
            print(f"💥 Unexpected error: {str(e)}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(description="Webhook Test Script")
    parser.add_argument("--url", type=str, required=True, help="Document URL to test")
    parser.add_argument("--questions", type=str, nargs='+', required=True, help="Questions to ask about the document")
    parser.add_argument("--api-base", type=str, default="http://localhost:8000", help="API base URL")
    parser.add_argument("--output", type=str, help="Output file for results")
    parser.add_argument("--json", action="store_true", help="Output only JSON (no verbose logging)")
    
    args = parser.parse_args()
    
    # Test the webhook
    result = test_webhook(
        args.api_base,
        args.url,
        args.questions,
        verbose=not args.json
    )
    
    # Output results
    if args.json:
        print(json.dumps(result, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        if not args.json:
            print(f"📁 Results saved to {args.output}")

# Example usage
if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Interactive demo
        print("🔗 Webhook Test Demo")
        print("=" * 40)
        
        # Demo with sample data
        demo_url = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
        demo_questions = [
            "What is the grace period for premium payment?",
            "What is the waiting period for maternity benefits?"
        ]
        
        result = test_webhook(
            "http://localhost:8000",
            demo_url,
            demo_questions,
            verbose=True
        )
        
        if result["success"]:
            print("\n✅ Webhook demo completed successfully!")
        else:
            print("\n❌ Webhook demo failed!")
    else:
        main()
