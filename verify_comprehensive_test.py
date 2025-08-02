"""
Quick test to verify comprehensive test setup works
"""
import requests
import time

def test_comprehensive_setup():
    """Test if comprehensive test can connect to the system"""
    
    # Test URL
    ngrok_url = "https://bbf70119fe3c.ngrok-free.app"
    webhook_url = f"{ngrok_url}/api/v1/webhook/test"
    health_url = f"{ngrok_url}/health"
    
    headers = {
        "Authorization": "Bearer 1fcad8c4ef8f698546d9a985893a9bfa5c60c562930511aa5c5e2ac8366de6fc",
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing Comprehensive Test Setup")
    print("=" * 40)
    
    # Health check
    try:
        print("🏥 Health Check...")
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data.get('status', 'unknown')}")
            print(f"📋 Service: {data.get('service', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test single question processing
    try:
        print("\n📋 Testing Document Processing...")
        
        payload = {
            "documents": "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D",
            "questions": ["What is the policy name?"]
        }
        
        start_time = time.time()
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=60)
        processing_time = time.time() - start_time
        
        print(f"⏱️ Response Time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            answers = data.get("answers", [])
            
            print(f"✅ Success: {success}")
            if answers:
                answer = answers[0]
                print(f"📝 Answer: {answer[:100]}...")
                
                # Check for errors
                if any(error_word in answer.lower() for error_word in ['error', 'unable', '429', 'quota']):
                    print("⚠️ Warning: Answer contains error indicators")
                    return False
                else:
                    print("✅ Answer looks good!")
                    return True
            else:
                print("❌ No answers received")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"📝 Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_comprehensive_setup()
    
    if success:
        print("\n🎉 Comprehensive test setup is working!")
        print("✅ Ready to run full comprehensive test")
    else:
        print("\n❌ Issues with comprehensive test setup")
        print("🔧 Please check server and API configuration")
