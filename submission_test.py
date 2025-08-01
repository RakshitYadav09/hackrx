"""
Automated Test Script for Submission Requirements

This script is designed to work with automated test cases from submission pages.
It provides clean JSON output suitable for programmatic evaluation.
"""
import requests
import json
import sys
import argparse
from typing import List, Dict

class SubmissionTester:
    def __init__(self, api_base_url: str = "http://localhost:8000", api_token: str = "1fcad8c4ef8f698546d9a985893a9bfa5c60c562930511aa5c5e2ac8366de6fc"):
        self.api_base_url = api_base_url
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def process_document(self, document_url: str, questions: List[str]) -> Dict:
        """
        Process a document with questions and return structured results
        
        Args:
            document_url (str): URL to the PDF document
            questions (List[str]): List of questions to ask
            
        Returns:
            Dict: Structured response with answers or error information
        """
        
        payload = {
            "documents": document_url,
            "questions": questions
        }
        
        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/hackrx/run",
                headers=self.headers,
                json=payload,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "document_url": document_url,
                    "questions": questions,
                    "answers": result["answers"],
                    "processing_time": result.get("processing_time"),
                    "total_chunks": result.get("total_chunks"),
                    "timestamp": result.get("timestamp")
                }
            else:
                error_detail = response.json() if 'application/json' in response.headers.get('content-type', '') else response.text
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_detail}",
                    "document_url": document_url,
                    "questions": questions
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout (300 seconds)",
                "document_url": document_url,
                "questions": questions
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "document_url": document_url,
                "questions": questions
            }
    
    def batch_process(self, test_cases: List[Dict]) -> List[Dict]:
        """
        Process multiple test cases
        
        Args:
            test_cases (List[Dict]): List of test cases with 'document_url' and 'questions'
            
        Returns:
            List[Dict]: Results for each test case
        """
        results = []
        
        for i, test_case in enumerate(test_cases):
            result = self.process_document(
                test_case["documents"],
                test_case["questions"]
            )
            result["test_case_id"] = i + 1
            results.append(result)
        
        return results
    
    def check_system_health(self) -> bool:
        """Check if the system is healthy and ready"""
        try:
            response = requests.get(
                f"{self.api_base_url}/api/v1/status",
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

def main():
    parser = argparse.ArgumentParser(description="Automated Test Script for Submission")
    parser.add_argument("--url", type=str, help="Single document URL to test")
    parser.add_argument("--questions", type=str, nargs='+', help="Questions to ask about the document")
    parser.add_argument("--config", type=str, help="JSON file with test configuration")
    parser.add_argument("--output", type=str, help="Output file for results")
    parser.add_argument("--api-base", type=str, default="http://localhost:8000", help="API base URL")
    parser.add_argument("--api-token", type=str, default="1fcad8c4ef8f698546d9a985893a9bfa5c60c562930511aa5c5e2ac8366de6fc", help="API token")
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = SubmissionTester(args.api_base, args.api_token)
    
    # Check system health
    if not tester.check_system_health():
        result = {
            "success": False,
            "error": "System is not healthy or not running"
        }
        print(json.dumps(result))
        sys.exit(1)
    
    # Process based on input method
    if args.config:
        # Load test cases from JSON file
        try:
            with open(args.config, 'r') as f:
                test_config = json.load(f)
            
            if "test_cases" in test_config:
                results = tester.batch_process(test_config["test_cases"])
            else:
                # Single test case format
                results = [tester.process_document(test_config["documents"], test_config["questions"])]
        
        except Exception as e:
            result = {
                "success": False,
                "error": f"Failed to load config file: {str(e)}"
            }
            print(json.dumps(result))
            sys.exit(1)
    
    elif args.url and args.questions:
        # Single test case from command line
        results = [tester.process_document(args.url, args.questions)]
    
    else:
        # Interactive mode or show usage
        result = {
            "success": False,
            "error": "Please provide either --config file or --url with --questions"
        }
        print(json.dumps(result))
        sys.exit(1)
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
