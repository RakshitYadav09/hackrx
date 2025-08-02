"""
Simple Test Suite for HackRX Document Query System
Tests basic functionality, health check, and document processing
"""

import requests
import json
import time
from datetime import datetime

class SimpleSystemTest:
    def __init__(self):
        # Use localhost for testing (make sure server is running on port 8001)
        self.base_url = "http://localhost:8001"
        self.webhook_url = f"{self.base_url}/api/v1/webhook/test"
        self.health_url = f"{self.base_url}/health"
        self.headers = {
            "Authorization": "Bearer 1fcad8c4ef8f698546d9a985893a9bfa5c60c562930511aa5c5e2ac8366de6fc",
            "Content-Type": "application/json"
        }
        
        # Simple test document
        self.test_document = {
            "name": "Arogya Sanjeevani Policy",
            "url": "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D",
            "questions": [
                "What is the policy name?",
                "What is the sum insured amount?"
            ]
        }

    def test_health_check(self):
        """Test if the server is running and healthy."""
        print("🏥 Testing Health Check...")
        try:
            response = requests.get(self.health_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server Status: {data.get('status', 'unknown')}")
                print(f"📋 Service: {data.get('service', 'unknown')}")
                print(f"🔢 Version: {data.get('version', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    def test_document_processing(self):
        """Test document processing with a simple question."""
        print(f"\n📋 Testing Document Processing...")
        print(f"📄 Document: {self.test_document['name']}")
        print(f"❓ Questions: {len(self.test_document['questions'])}")
        
        payload = {
            "documents": self.test_document["url"],
            "questions": self.test_document["questions"]
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                self.webhook_url, 
                json=payload, 
                headers=self.headers, 
                timeout=120
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Response time: {processing_time:.2f}s")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data.get('success', False)}")
                print(f"🖥️ Server processing time: {data.get('processing_time', 0):.2f}s")
                
                answers = data.get('answers', [])
                confidence_scores = data.get('confidence_scores', [])
                
                success_count = 0
                for i, (question, answer) in enumerate(zip(self.test_document['questions'], answers)):
                    confidence = confidence_scores[i] if i < len(confidence_scores) else 0.0
                    
                    # Check if answer contains error messages
                    if any(error_word in answer.lower() for error_word in ['error', 'unable', 'failed', '429', 'quota']):
                        print(f"   Q{i+1}: {question}")
                        print(f"   ❌ ERROR: {answer[:100]}...")
                        print(f"   📊 Confidence: {confidence:.2f}")
                    else:
                        print(f"   Q{i+1}: {question}")
                        print(f"   ✅ Answer: {answer[:100]}...")
                        print(f"   📊 Confidence: {confidence:.2f}")
                        success_count += 1
                
                success_rate = (success_count / len(answers)) * 100 if answers else 0
                print(f"\n📊 SUCCESS RATE: {success_rate:.1f}% ({success_count}/{len(answers)})")
                
                return success_rate > 0
                
            else:
                print(f"❌ Request failed with status: {response.status_code}")
                print(f"📝 Response: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            return False

    def run_all_tests(self):
        """Run all tests and provide summary."""
        print("🧪 HACKRX SYSTEM TEST SUITE")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        tests_passed = 0
        total_tests = 2
        
        # Test 1: Health Check
        if self.test_health_check():
            tests_passed += 1
        
        # Test 2: Document Processing
        if self.test_document_processing():
            tests_passed += 1
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
        print(f"📈 Success Rate: {(tests_passed/total_tests)*100:.1f}%")
        
        if tests_passed == total_tests:
            print("🎉 ALL TESTS PASSED! System is working correctly.")
            print("✅ Your HackRX system is ready for production!")
        elif tests_passed > 0:
            print("⚠️ Some tests passed. Check the errors above.")
        else:
            print("❌ All tests failed. Please check your configuration.")
            print("🔍 Make sure:")
            print("   • Server is running on port 8001")
            print("   • API key is valid and has quota")
            print("   • .env file is properly configured")
        
        return tests_passed == total_tests

if __name__ == "__main__":
    print("🚀 Starting HackRX System Tests...")
    print("📝 Note: Make sure your server is running on localhost:8001")
    print()
    
    tester = SimpleSystemTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 READY FOR DEPLOYMENT!")
    else:
        print("\n🔧 PLEASE FIX ISSUES BEFORE DEPLOYMENT")
