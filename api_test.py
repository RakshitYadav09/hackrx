"""
API Test Script for LLM-Powered Query Retrieval System

This script allows you to test the system with your own PDF URLs and questions.
Perfect for testing against submission requirements and automated test cases.
"""
import requests
import json
import sys
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
API_TOKEN = "1fcad8c4ef8f698546d9a985893a9bfa5c60c562930511aa5c5e2ac8366de6fc"

def test_api_endpoint(document_url: str, questions: list, verbose: bool = True):
    """
    Test the API with a document URL and list of questions
    
    Args:
        document_url (str): URL to the PDF document
        questions (list): List of questions to ask about the document
        verbose (bool): Whether to print detailed output
    
    Returns:
        dict: API response or error information
    """
    
    if verbose:
        print("🔄 Testing LLM-Powered Query Retrieval System")
        print("=" * 60)
        print(f"📄 Document: {document_url}")
        print(f"❓ Questions: {len(questions)}")
        print("-" * 60)
    
    # Prepare the request
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "documents": document_url,
        "questions": questions
    }
    
    try:
        if verbose:
            print("🚀 Sending request to API...")
        
        # Make the API call
        response = requests.post(
            f"{API_BASE_URL}/api/v1/hackrx/run",
            headers=headers,
            json=payload,
            timeout=300  # 5 minutes timeout for large documents
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if verbose:
                print("✅ Request successful!")
                print("\n📋 Results:")
                print("=" * 60)
                
                for i, (question, answer) in enumerate(zip(questions, result["answers"]), 1):
                    print(f"\n🔍 Question {i}:")
                    print(f"   {question}")
                    print(f"\n💡 Answer {i}:")
                    print(f"   {answer}")
                    print("-" * 40)
                
                print(f"\n⏱️  Processing time: {result.get('processing_time', 'N/A')} seconds")
                print(f"📊 Total chunks processed: {result.get('total_chunks', 'N/A')}")
            
            return {
                "success": True,
                "data": result
            }
        
        else:
            error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            if verbose:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"Error: {error_detail}")
            
            return {
                "success": False,
                "status_code": response.status_code,
                "error": error_detail
            }
    
    except requests.exceptions.Timeout:
        if verbose:
            print("⏰ Request timed out (5 minutes). Document might be too large.")
        return {"success": False, "error": "Request timeout"}
    
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"🔌 Connection error: {str(e)}")
        return {"success": False, "error": f"Connection error: {str(e)}"}
    
    except Exception as e:
        if verbose:
            print(f"💥 Unexpected error: {str(e)}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def check_system_status():
    """Check if the API system is running and healthy"""
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = requests.get(f"{API_BASE_URL}/api/v1/status", headers=headers, timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            print("✅ System Status: OPERATIONAL")
            print(f"   - PDF Processor: {status['components']['pdf_processor']}")
            print(f"   - Vector DB: {status['components']['vector_db']['type']} ({status['components']['vector_db']['status']})")
            print(f"   - LLM Model: {status['components']['llm_processor']['model']} ({status['components']['llm_processor']['status']})")
            return True
        else:
            print(f"❌ System Status: ERROR ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to system: {str(e)}")
        return False

def run_sample_tests():
    """Run sample tests with predefined documents and questions"""
    
    print("🧪 Running Sample Tests")
    print("=" * 60)
    
    # Sample test cases
    test_cases = [
        {
            "name": "Insurance Policy Test",
            "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "questions": [
                "What is the grace period for premium payment?",
                "What is the waiting period for pre-existing diseases?",
                "What are the coverage limits for room rent?"
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test Case {i}: {test_case['name']}")
        print("=" * 40)
        
        result = test_api_endpoint(
            test_case["document_url"],
            test_case["questions"],
            verbose=True
        )
        
        if result["success"]:
            print("✅ Test PASSED")
        else:
            print("❌ Test FAILED")
            print(f"Error: {result['error']}")

def run_custom_test():
    """Interactive mode for custom testing"""
    
    print("🎯 Custom Test Mode")
    print("=" * 60)
    
    # Get document URL
    document_url = input("📄 Enter PDF document URL: ").strip()
    if not document_url:
        print("❌ Document URL is required!")
        return
    
    # Get questions
    print("\n❓ Enter your questions (one per line, empty line to finish):")
    questions = []
    while True:
        question = input(f"   Question {len(questions) + 1}: ").strip()
        if not question:
            break
        questions.append(question)
    
    if not questions:
        print("❌ At least one question is required!")
        return
    
    print(f"\n🚀 Testing with {len(questions)} questions...")
    
    result = test_api_endpoint(document_url, questions, verbose=True)
    
    if result["success"]:
        print("\n✅ Custom test completed successfully!")
        
        # Option to save results
        save = input("\n💾 Save results to file? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"test_results_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(result["data"], f, indent=2)
            print(f"📁 Results saved to {filename}")
    
    else:
        print("\n❌ Custom test failed!")

def automated_test_format(document_url: str, questions: list):
    """
    Format for automated testing - returns JSON response suitable for submission
    
    This function is designed to work with automated test cases where you need
    clean JSON output without verbose logging.
    """
    result = test_api_endpoint(document_url, questions, verbose=False)
    
    if result["success"]:
        return {
            "status": "success",
            "answers": result["data"]["answers"],
            "processing_time": result["data"].get("processing_time"),
            "total_chunks": result["data"].get("total_chunks")
        }
    else:
        return {
            "status": "error",
            "error": result["error"]
        }

if __name__ == "__main__":
    print("🤖 LLM-Powered Query Retrieval System - API Tester")
    print("=" * 70)
    
    # Check system status first
    if not check_system_status():
        print("\n❌ System is not running. Please start the server first:")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    print("\n🎯 Choose test mode:")
    print("1. Run sample tests")
    print("2. Custom test (interactive)")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            run_sample_tests()
            break
        elif choice == "2":
            run_custom_test()
            break
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

# Example usage for automated testing:
"""
# For submission/automated testing, use this format:
if __name__ == "__main__":
    document_url = "your_test_document_url_here"
    questions = ["Question 1", "Question 2", "Question 3"]
    
    result = automated_test_format(document_url, questions)
    print(json.dumps(result, indent=2))
"""
