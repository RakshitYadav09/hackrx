"""
Comprehensive Test Suite for Multi-Document Accuracy Assessment
Tests the system against 4 diverse document types:
1. Arogya Sanjeevani Policy (Insurance)
2. HDFC Life Insurance Policy (Insurance)
3. Indian Constitution (Legal)
4. Principia Mathematica (Scientific)
"""
import requests
import json
import time
from datetime import datetime
import statistics

class ComprehensiveTestSuite:
    def __init__(self):
        self.ngrok_url = "https://bbf70119fe3c.ngrok-free.app"
        self.webhook_url = f"{self.ngrok_url}/api/v1/webhook/test"
        self.headers = {
            "Authorization": "Bearer 1fcad8c4ef8f698546d9a985893a9bfa5c60c562930511aa5c5e2ac8366de6fc",
            "Content-Type": "application/json"
        }
        
        # Test documents with their expected characteristics
        self.test_documents = {
            "arogya_sanjeevani": {
                "url": "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D",
                "type": "insurance_policy",
                "questions": [
                    {
                        "question": "What is the sum insured amount mentioned in the policy?",
                        "expected_keywords": ["₹", "lakh", "amount", "sum insured", "coverage"],
                        "weight": 10
                    },
                    {
                        "question": "What are the key benefits covered under this policy?",
                        "expected_keywords": ["hospitalization", "medical", "treatment", "coverage", "benefits"],
                        "weight": 9
                    },
                    {
                        "question": "What are the waiting periods for different conditions?",
                        "expected_keywords": ["30 days", "waiting period", "months", "pre-existing"],
                        "weight": 8
                    },
                    {
                        "question": "What exclusions are mentioned in the policy?",
                        "expected_keywords": ["exclusions", "not covered", "excluded", "except"],
                        "weight": 7
                    },
                    {
                        "question": "What is the policy renewal process?",
                        "expected_keywords": ["renewal", "renew", "annually", "premium"],
                        "weight": 6
                    }
                ]
            },
            "hdfc_life": {
                "url": "https://hackrx.blob.core.windows.net/assets/hackrx_6/policies/HDFHLIP23024V072223.pdf?sv=2023-01-03&st=2025-07-30T06%3A46%3A49Z&se=2025-09-01T06%3A46%3A00Z&sr=c&sp=rl&sig=9szykRKdGYj0BVm1skP%2BX8N9%2FRENEn2k7MQPUp33jyQ%3D",
                "type": "life_insurance",
                "questions": [
                    {
                        "question": "What is the policy term and premium payment term?",
                        "expected_keywords": ["years", "term", "premium", "payment", "policy period"],
                        "weight": 10
                    },
                    {
                        "question": "What are the death benefits provided?",
                        "expected_keywords": ["death benefit", "sum assured", "beneficiary", "nominee"],
                        "weight": 9
                    },
                    {
                        "question": "What are the maturity benefits?",
                        "expected_keywords": ["maturity", "survival benefit", "guaranteed", "return"],
                        "weight": 8
                    },
                    {
                        "question": "What are the surrender value provisions?",
                        "expected_keywords": ["surrender", "cash value", "guaranteed surrender value"],
                        "weight": 7
                    },
                    {
                        "question": "What are the eligibility criteria for this policy?",
                        "expected_keywords": ["age", "minimum", "maximum", "entry", "eligibility"],
                        "weight": 6
                    }
                ]
            },
            "indian_constitution": {
                "url": "https://hackrx.blob.core.windows.net/assets/indian_constitution.pdf?sv=2023-01-03&st=2025-07-28T06%3A42%3A00Z&se=2026-11-29T06%3A42%3A00Z&sr=b&sp=r&sig=5Gs%2FOXqP3zY00lgciu4BZjDV5QjTDIx7fgnfdz6Pu24%3D",
                "type": "legal_document",
                "questions": [
                    {
                        "question": "What are the fundamental rights mentioned in the Constitution?",
                        "expected_keywords": ["fundamental rights", "right to", "equality", "freedom", "life"],
                        "weight": 10
                    },
                    {
                        "question": "What is the structure of the Indian Parliament?",
                        "expected_keywords": ["parliament", "lok sabha", "rajya sabha", "bicameral"],
                        "weight": 9
                    },
                    {
                        "question": "What are the directive principles of state policy?",
                        "expected_keywords": ["directive principles", "state policy", "welfare", "social"],
                        "weight": 8
                    },
                    {
                        "question": "What is the process for constitutional amendments?",
                        "expected_keywords": ["amendment", "article", "procedure", "majority"],
                        "weight": 7
                    },
                    {
                        "question": "What is the role of the President of India?",
                        "expected_keywords": ["president", "executive", "powers", "head of state"],
                        "weight": 6
                    }
                ]
            },
            "principia_newton": {
                "url": "https://hackrx.blob.core.windows.net/assets/principia_newton.pdf?sv=2023-01-03&st=2025-07-28T07%3A20%3A32Z&se=2026-07-29T07%3A20%3A00Z&sr=b&sp=r&sig=V5I1QYyigoxeUMbnUKsdEaST99F5%2FDfo7wpKg9XXF5w%3D",
                "type": "scientific_text",
                "questions": [
                    {
                        "question": "What are Newton's three laws of motion?",
                        "expected_keywords": ["first law", "second law", "third law", "motion", "force"],
                        "weight": 10
                    },
                    {
                        "question": "What is the law of universal gravitation?",
                        "expected_keywords": ["gravitation", "universal", "gravity", "mass", "distance"],
                        "weight": 9
                    },
                    {
                        "question": "What mathematical principles are discussed?",
                        "expected_keywords": ["mathematics", "calculus", "geometry", "principles"],
                        "weight": 8
                    },
                    {
                        "question": "What are the concepts related to planetary motion?",
                        "expected_keywords": ["planetary", "orbit", "celestial", "motion", "ellipse"],
                        "weight": 7
                    },
                    {
                        "question": "What experimental methods are described?",
                        "expected_keywords": ["experiment", "observation", "method", "demonstration"],
                        "weight": 6
                    }
                ]
            }
        }
        
        self.test_results = []
        self.document_scores = {}
    
    def calculate_accuracy_score(self, answer, expected_keywords, weight):
        """Calculate accuracy score based on keyword presence and answer quality"""
        if not answer:
            return 0
        
        answer_lower = answer.lower()
        
        # Keyword matching score (40% of total)
        keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
        keyword_score = (keyword_matches / len(expected_keywords)) * 0.4
        
        # Answer length and substance score (30% of total)
        min_length = 50
        max_length = 500
        length_score = min(len(answer) / max_length, 1.0) * 0.3
        
        # Coherence and relevance score (30% of total)
        # Check for common phrases that indicate good understanding
        quality_indicators = [
            "according to", "mentioned", "stated", "provides", "includes",
            "specifically", "detailed", "comprehensive", "section", "clause"
        ]
        quality_matches = sum(1 for indicator in quality_indicators if indicator in answer_lower)
        coherence_score = min(quality_matches / 5, 1.0) * 0.3
        
        total_score = (keyword_score + length_score + coherence_score) * weight * 10
        return min(total_score, 10.0)  # Cap at 10
    
    def test_document(self, doc_name, doc_info):
        """Test a single document with all its questions"""
        print(f"\n📋 Testing Document: {doc_name.upper().replace('_', ' ')}")
        print(f"📄 Type: {doc_info['type']}")
        print("="*60)
        
        doc_scores = []
        question_results = []
        
        for i, q_info in enumerate(doc_info['questions'], 1):
            print(f"\nQ{i}: {q_info['question']}")
            
            try:
                payload = {
                    "documents": doc_info['url'],
                    "questions": [q_info['question']]
                }
                
                start_time = time.time()
                response = requests.post(self.webhook_url, json=payload, headers=self.headers, timeout=120)
                processing_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answers", [""])[0]
                    
                    if answer:
                        accuracy_score = self.calculate_accuracy_score(
                            answer, q_info['expected_keywords'], q_info['weight']
                        )
                        doc_scores.append(accuracy_score)
                        
                        # Check keyword presence
                        found_keywords = [kw for kw in q_info['expected_keywords'] 
                                        if kw.lower() in answer.lower()]
                        
                        # Check for API errors
                        has_error = any(error_word in answer.lower() for error_word in 
                                      ['error', 'unable', '429', 'quota', 'failed', 'technical error'])
                        
                        if has_error:
                            status = "❌ ERROR"
                            accuracy_score = 0  # Set to 0 for errors
                            doc_scores[-1] = 0  # Update the score
                        else:
                            status = "✅" if accuracy_score >= 7 else "⚠️" if accuracy_score >= 4 else "❌"
                        
                        print(f"   {status} Score: {accuracy_score:.1f}/10 | Time: {processing_time:.1f}s")
                        print(f"   🔍 Keywords found: {len(found_keywords)}/{len(q_info['expected_keywords'])}")
                        print(f"   📝 Answer: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                        
                        question_results.append({
                            "question": q_info['question'],
                            "answer": answer,
                            "score": accuracy_score,
                            "keywords_found": len(found_keywords),
                            "total_keywords": len(q_info['expected_keywords']),
                            "processing_time": processing_time,
                            "has_error": has_error
                        })
                    else:
                        print(f"   ❌ No answer received")
                        doc_scores.append(0)
                elif response.status_code == 422:
                    print(f"   ❌ Request Error (422): Invalid request format")
                    print(f"   📝 Details: {response.text[:200]}...")
                    doc_scores.append(0)
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    print(f"   📝 Response: {response.text[:200]}...")
                    doc_scores.append(0)
                    
            except requests.exceptions.Timeout:
                print(f"   ❌ Timeout: Request took longer than 120 seconds")
                doc_scores.append(0)
            except requests.exceptions.ConnectionError:
                print(f"   ❌ Connection Error: Cannot reach server")
                doc_scores.append(0)
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                doc_scores.append(0)
        
        # Calculate document statistics
        if doc_scores:
            avg_score = statistics.mean(doc_scores)
            max_score = max(doc_scores)
            min_score = min(doc_scores)
            
            print(f"\n📊 Document Summary:")
            print(f"   Average Score: {avg_score:.1f}/10")
            print(f"   Best Score: {max_score:.1f}/10")
            print(f"   Worst Score: {min_score:.1f}/10")
            print(f"   Questions Passed (≥7): {sum(1 for s in doc_scores if s >= 7)}/{len(doc_scores)}")
            
            self.document_scores[doc_name] = {
                "average": avg_score,
                "max": max_score,
                "min": min_score,
                "scores": doc_scores,
                "questions": question_results,
                "type": doc_info['type']
            }
    
    def test_cross_document_analysis(self):
        """Test cross-document analysis capabilities"""
        print(f"\n🔄 CROSS-DOCUMENT ANALYSIS")
        print("="*60)
        
        # Test document type recognition
        type_questions = [
            {
                "doc": "arogya_sanjeevani",
                "question": "What type of document is this?",
                "expected": ["insurance", "policy", "medical", "health"]
            },
            {
                "doc": "indian_constitution",
                "question": "What type of document is this?", 
                "expected": ["constitution", "legal", "law", "government"]
            }
        ]
        
        for test in type_questions:
            doc_info = self.test_documents[test["doc"]]
            payload = {
                "documents": doc_info['url'],
                "questions": [test['question']]
            }
            
            try:
                response = requests.post(self.webhook_url, json=payload, headers=self.headers, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answers", [""])[0]
                    
                    found_keywords = [kw for kw in test['expected'] if kw.lower() in answer.lower()]
                    accuracy = len(found_keywords) / len(test['expected']) * 10
                    
                    status = "✅" if accuracy >= 7 else "⚠️" if accuracy >= 4 else "❌"
                    print(f"{status} {test['doc']}: {accuracy:.1f}/10 - {answer[:80]}...")
                    
            except Exception as e:
                print(f"❌ {test['doc']}: Error - {str(e)}")
    
    def test_complex_reasoning(self):
        """Test complex reasoning capabilities"""
        print(f"\n🧠 COMPLEX REASONING TESTS")
        print("="*60)
        
        complex_tests = [
            {
                "doc": "arogya_sanjeevani",
                "question": "If someone has a pre-existing condition, how long do they need to wait before it's covered, and what are the implications?",
                "expected": ["pre-existing", "waiting", "months", "years", "coverage"]
            },
            {
                "doc": "indian_constitution", 
                "question": "How do fundamental rights and directive principles complement each other in governance?",
                "expected": ["fundamental rights", "directive principles", "governance", "complement"]
            }
        ]
        
        reasoning_scores = []
        for test in complex_tests:
            doc_info = self.test_documents[test["doc"]]
            payload = {
                "documents": doc_info['url'],
                "questions": [test['question']]
            }
            
            try:
                response = requests.post(self.webhook_url, json=payload, headers=self.headers, timeout=90)
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answers", [""])[0]
                    
                    # Score based on complexity and depth
                    complexity_score = self.calculate_accuracy_score(answer, test['expected'], 1.0)
                    reasoning_scores.append(complexity_score)
                    
                    status = "✅" if complexity_score >= 7 else "⚠️" if complexity_score >= 4 else "❌"
                    print(f"{status} {test['doc']}: {complexity_score:.1f}/10")
                    print(f"   📝 {answer[:120]}...")
                    
            except Exception as e:
                print(f"❌ {test['doc']}: Error - {str(e)}")
                reasoning_scores.append(0)
        
        if reasoning_scores:
            avg_reasoning = statistics.mean(reasoning_scores)
            print(f"\n🧠 Average Reasoning Score: {avg_reasoning:.1f}/10")
            return avg_reasoning
        return 0
    
    def generate_comprehensive_report(self):
        """Generate detailed performance report with improvement recommendations"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE ACCURACY ASSESSMENT REPORT")
        print("="*80)
        
        if not self.document_scores:
            print("❌ No test results available")
            return
        
        # Overall statistics
        all_scores = []
        document_averages = []
        
        for doc_name, results in self.document_scores.items():
            all_scores.extend(results['scores'])
            document_averages.append(results['average'])
        
        overall_avg = statistics.mean(all_scores) if all_scores else 0
        overall_std = statistics.stdev(all_scores) if len(all_scores) > 1 else 0
        
        print(f"🎯 OVERALL PERFORMANCE")
        print(f"   Average Accuracy: {overall_avg:.1f}/10")
        print(f"   Standard Deviation: {overall_std:.1f}")
        print(f"   Questions Scoring ≥7: {sum(1 for s in all_scores if s >= 7)}/{len(all_scores)} ({(sum(1 for s in all_scores if s >= 7)/len(all_scores)*100):.1f}%)")
        print(f"   Questions Scoring ≥5: {sum(1 for s in all_scores if s >= 5)}/{len(all_scores)} ({(sum(1 for s in all_scores if s >= 5)/len(all_scores)*100):.1f}%)")
        
        # Document-wise performance
        print(f"\n📋 DOCUMENT-WISE PERFORMANCE")
        for doc_name, results in self.document_scores.items():
            print(f"\n📄 {doc_name.upper().replace('_', ' ')} ({results['type']})")
            print(f"   Average: {results['average']:.1f}/10")
            print(f"   Range: {results['min']:.1f} - {results['max']:.1f}")
            print(f"   Success Rate: {sum(1 for s in results['scores'] if s >= 7)}/{len(results['scores'])}")
        
        # Performance by document type
        print(f"\n📈 PERFORMANCE BY DOCUMENT TYPE")
        type_performance = {}
        for doc_name, results in self.document_scores.items():
            doc_type = results['type']
            if doc_type not in type_performance:
                type_performance[doc_type] = []
            type_performance[doc_type].extend(results['scores'])
        
        for doc_type, scores in type_performance.items():
            avg_score = statistics.mean(scores)
            print(f"   {doc_type.replace('_', ' ').title()}: {avg_score:.1f}/10")
        
        # Identify improvement areas
        print(f"\n🔧 IMPROVEMENT RECOMMENDATIONS")
        
        weak_areas = []
        for doc_name, results in self.document_scores.items():
            for question in results['questions']:
                if question['score'] < 5:
                    weak_areas.append({
                        'document': doc_name,
                        'question': question['question'],
                        'score': question['score'],
                        'type': results['type']
                    })
        
        if weak_areas:
            print(f"   📉 {len(weak_areas)} questions scored below 5/10")
            
            # Group by document type
            type_issues = {}
            for issue in weak_areas:
                doc_type = issue['type']
                if doc_type not in type_issues:
                    type_issues[doc_type] = []
                type_issues[doc_type].append(issue)
            
            for doc_type, issues in type_issues.items():
                print(f"   🔴 {doc_type.replace('_', ' ').title()}: {len(issues)} weak questions")
        
        # System recommendations
        print(f"\n💡 SYSTEM ENHANCEMENT SUGGESTIONS")
        
        if overall_avg < 5:
            print("   🚨 CRITICAL: System accuracy below 50% - Major improvements needed")
            print("   📋 Recommended Actions:")
            print("      • Implement document-specific processing pipelines")
            print("      • Add domain-specific prompt engineering")
            print("      • Improve PDF text extraction quality")
            print("      • Add semantic chunking and better context retrieval")
        elif overall_avg < 7:
            print("   ⚠️ MODERATE: System accuracy 50-70% - Significant improvements needed")
            print("   📋 Recommended Actions:")
            print("      • Fine-tune prompts for different document types")
            print("      • Implement better keyword extraction")
            print("      • Add context-aware answer generation")
        else:
            print("   ✅ GOOD: System accuracy >70% - Minor optimizations needed")
            print("   📋 Recommended Actions:")
            print("      • Fine-tune edge cases")
            print("      • Optimize processing speed")
            print("      • Add confidence scoring")
        
        # Final assessment
        print(f"\n🏆 FINAL ASSESSMENT")
        if overall_avg >= 7:
            grade = "A"
            status = "EXCELLENT"
        elif overall_avg >= 6:
            grade = "B"
            status = "GOOD"
        elif overall_avg >= 5:
            grade = "C" 
            status = "ACCEPTABLE"
        else:
            grade = "D"
            status = "NEEDS IMPROVEMENT"
        
        print(f"   Grade: {grade}")
        print(f"   Status: {status}")
        print(f"   Target Achieved: {'✅ YES' if overall_avg >= 5 else '❌ NO'} (Target: 50%+ accuracy)")
        
        return overall_avg
    
    def run_full_test_suite(self):
        """Run the complete test suite"""
        print("🚀 STARTING COMPREHENSIVE MULTI-DOCUMENT ACCURACY ASSESSMENT")
        print(f"🌐 Testing System: {self.ngrok_url}")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Initial system verification
        print("🏥 System Verification...")
        try:
            health_response = requests.get(f"{self.ngrok_url}/health", timeout=10)
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ Server: {health_data.get('status', 'unknown')}")
                print(f"📋 Service: {health_data.get('service', 'unknown')}")
                print(f"🔢 Version: {health_data.get('version', 'unknown')}")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                print("⚠️ Continuing with tests anyway...")
        except Exception as e:
            print(f"⚠️ Health check error: {e}")
            print("⚠️ Continuing with tests anyway...")
        
        print("\n🎯 Starting Document Tests...")
        
        # Test each document
        for doc_name, doc_info in self.test_documents.items():
            self.test_document(doc_name, doc_info)
        
        # Run additional tests
        self.test_cross_document_analysis()
        reasoning_score = self.test_complex_reasoning()
        
        # Generate final report
        overall_score = self.generate_comprehensive_report()
        
        return overall_score

if __name__ == "__main__":
    test_suite = ComprehensiveTestSuite()
    final_score = test_suite.run_full_test_suite()
