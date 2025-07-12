#!/usr/bin/env python3
"""
Test AI enhancement API endpoints with authentication
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def login():
    """Login and get JWT token"""
    login_data = {
        "username": "demo@vulnpatch.ai",
        "password": "demo123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_cache_stats(token):
    """Test cache statistics endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/v1/ai/cache/stats", headers=headers)
    print(f"\n🔍 Testing Cache Stats Endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Cache stats retrieved successfully")
        print(f"Cache features: {len(data.get('cache_features', []))}")
        print(f"Performance benefits: {len(data.get('performance_benefits', []))}")
        return True
    else:
        print(f"❌ Cache stats failed: {response.text}")
        return False

def test_performance_metrics(token):
    """Test performance metrics endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/v1/ai/performance/metrics", headers=headers)
    print(f"\n🔍 Testing Performance Metrics Endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Performance metrics retrieved successfully")
        print(f"AI features active: {len(data.get('ai_features_active', []))}")
        print(f"Optimization recommendations: {len(data.get('optimization_recommendations', []))}")
        return True
    else:
        print(f"❌ Performance metrics failed: {response.text}")
        return False

def test_available_models(token):
    """Test available models endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/v1/ai/models/available", headers=headers)
    print(f"\n🔍 Testing Available Models Endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Available models retrieved successfully")
        print(f"Analysis types: {len(data.get('analysis_types', []))}")
        print(f"AI models: {len(data.get('ai_models', []))}")
        print(f"Features: {len(data.get('features', []))}")
        return True
    else:
        print(f"❌ Available models failed: {response.text}")
        return False

def test_suggested_questions(token):
    """Test suggested questions endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/api/v1/ai/suggest-questions", headers=headers)
    print(f"\n🔍 Testing Suggested Questions Endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Suggested questions retrieved successfully")
        print(f"Suggestions count: {len(data.get('suggestions', []))}")
        print(f"Context based: {data.get('context_based', False)}")
        return True
    else:
        print(f"❌ Suggested questions failed: {response.text}")
        return False

def test_ai_query(token):
    """Test AI query endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    query_data = {
        "query": "What are the most common types of vulnerabilities?",
        "context": {},
        "conversation_id": "test-conversation-123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/ai/query", headers=headers, json=query_data)
    print(f"\n🔍 Testing AI Query Endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ AI query processed successfully")
        print(f"Response length: {len(data.get('response', ''))}")
        print(f"Conversation ID: {data.get('conversation_id', 'None')}")
        return True
    else:
        print(f"❌ AI query failed: {response.text}")
        return False

def test_feedback_analytics(token):
    """Test feedback analytics endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/v1/ai/feedback/analytics?days=30", headers=headers)
    print(f"\n🔍 Testing Feedback Analytics Endpoint")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Feedback analytics retrieved successfully")
        print(f"Period: {data.get('period', 'Unknown')}")
        print(f"Analytics available: {data.get('analytics') is not None}")
        return True
    else:
        print(f"❌ Feedback analytics failed: {response.text}")
        return False

def main():
    """Run all API endpoint tests"""
    print("🚀 Starting AI Enhancement API Testing")
    print("=" * 50)
    
    # Login first
    print("🔐 Authenticating...")
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return False
    
    print("✅ Authentication successful")
    
    # Run tests
    tests = [
        ("Cache Stats", lambda: test_cache_stats(token)),
        ("Performance Metrics", lambda: test_performance_metrics(token)),
        ("Available Models", lambda: test_available_models(token)),
        ("Suggested Questions", lambda: test_suggested_questions(token)),
        ("AI Query", lambda: test_ai_query(token)),
        ("Feedback Analytics", lambda: test_feedback_analytics(token))
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 API ENDPOINT TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 OVERALL RESULT: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL API TESTS PASSED! Enhanced AI endpoints are working correctly.")
    else:
        print("⚠️  Some API tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)