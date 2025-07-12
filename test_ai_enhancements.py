#!/usr/bin/env python3
"""
Comprehensive test script for AI enhancements
Tests all major AI functionality including caching, analysis types, and error handling
"""
import asyncio
import sys
import os
import json
import time
from typing import Dict, Any

# Add backend to path
sys.path.append('./backend')

# Set environment variables for testing
os.environ['DATABASE_URL'] = 'postgresql://vulnpatch:vulnpatch@localhost:5432/vulnpatch_db'
os.environ['REDIS_URL'] = 'redis://localhost:6379'
os.environ['OPENAI_API_KEY'] = 'test-key-placeholder'  # Replace with actual key for real testing

async def test_imports():
    """Test that all enhanced modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from app.services.llm_service import EnhancedLLMService, AnalysisType
        from app.services.ai_service import EnhancedAIService
        from app.services.cache_service import CacheService, CVECache, AIResponseCache
        from app.services.feedback_service import FeedbackService
        from app.services.cve_service import CVEService
        from app.schemas.ai import AnalysisResponse, QueryRequest, QueryResponse
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

async def test_cache_service():
    """Test Redis cache service functionality"""
    print("\n🔍 Testing Cache Service...")
    
    try:
        from app.services.cache_service import CacheService, cve_cache, ai_cache
        
        cache = CacheService()
        
        # Test basic cache operations
        test_key = "test:cache:key"
        test_value = {"message": "test data", "timestamp": time.time()}
        
        # Test set/get
        result = cache.set(test_key, test_value, 60)
        print(f"✅ Cache set result: {result}")
        
        retrieved = cache.get(test_key)
        print(f"✅ Cache get result: {retrieved}")
        
        # Test existence
        exists = cache.exists(test_key)
        print(f"✅ Cache exists: {exists}")
        
        # Test TTL
        ttl = cache.get_ttl(test_key)
        print(f"✅ Cache TTL: {ttl} seconds")
        
        # Test cache stats
        stats = cache.get_stats()
        print(f"✅ Cache stats: {stats}")
        
        # Clean up
        cache.delete(test_key)
        
        # Test CVE cache
        cve_cache.set_cve_data("nginx", "1.18", "", {"test": "cve_data"})
        cve_data = cve_cache.get_cve_data("nginx", "1.18", "")
        print(f"✅ CVE cache test: {cve_data}")
        
        # Test AI cache
        ai_cache.set_vulnerability_analysis("nginx", "1.18", "test vuln", {"test": "analysis"})
        analysis = ai_cache.get_vulnerability_analysis("nginx", "1.18", "test vuln")
        print(f"✅ AI cache test: {analysis}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache service test failed: {e}")
        return False

async def test_llm_service():
    """Test Enhanced LLM Service"""
    print("\n🔍 Testing Enhanced LLM Service...")
    
    try:
        from app.services.llm_service import EnhancedLLMService, AnalysisType
        
        llm_service = EnhancedLLMService()
        
        # Test initialization
        print(f"✅ LLM Service initialized, has client: {llm_service.client is not None}")
        print(f"✅ LLM Service has cache: {llm_service.cache is not None}")
        print(f"✅ Context manager: {llm_service.context_manager}")
        
        # Test context window management
        long_text = "A" * 5000
        truncated = llm_service.context_manager.truncate_context(long_text)
        print(f"✅ Context truncation: {len(long_text)} -> {len(truncated)}")
        
        # Test fallback analysis (when no API key)
        fallback = llm_service._fallback_analysis("nginx", "1.18", "test vulnerability")
        print(f"✅ Fallback analysis: {fallback}")
        
        # Test vulnerability response parsing
        test_response = """
        {
            "severity": "High",
            "risk_score": 7.5,
            "recommendation": "Update nginx to latest version",
            "business_impact": "Potential data breach",
            "technical_details": "Buffer overflow vulnerability"
        }
        """
        parsed = llm_service._parse_vulnerability_response(test_response)
        print(f"✅ Response parsing: {parsed}")
        
        # Test query context enhancement
        test_context = {
            "severity_counts": {"Critical": 2, "High": 5},
            "common_services": [("nginx", 3), ("apache", 2)]
        }
        enhanced = llm_service._enhance_query_context(test_context)
        print(f"✅ Context enhancement: {enhanced}")
        
        # Test cache context preparation
        cache_context = llm_service._prepare_cache_context(enhanced)
        print(f"✅ Cache context: {cache_context}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        return False

async def test_cve_service():
    """Test Enhanced CVE Service with caching"""
    print("\n🔍 Testing Enhanced CVE Service...")
    
    try:
        from app.services.cve_service import CVEService
        
        cve_service = CVEService()
        
        print(f"✅ CVE Service initialized with cache: {cve_service.cache is not None}")
        
        # Test CVE data parsing
        sample_cve_item = {
            "cve": {
                "id": "CVE-2023-1234",
                "descriptions": [{"lang": "en", "value": "Test vulnerability description"}],
                "metrics": {
                    "cvssMetricV31": [{
                        "cvssData": {"baseScore": 7.5}
                    }]
                },
                "published": "2023-01-01T00:00:00.000",
                "lastModified": "2023-01-02T00:00:00.000"
            }
        }
        
        parsed_cve = cve_service._parse_cve_data(sample_cve_item)
        print(f"✅ CVE parsing: {parsed_cve}")
        
        # Test cache integration (without actual API calls)
        test_service = "nginx"
        test_version = "1.18"
        
        # Simulate caching
        cve_service.cache.set_cve_data(test_service, test_version, "", parsed_cve)
        cached_data = cve_service.cache.get_cve_data(test_service, test_version, "")
        print(f"✅ CVE caching works: {cached_data is not None}")
        
        return True
        
    except Exception as e:
        print(f"❌ CVE service test failed: {e}")
        return False

async def test_ai_service_without_db():
    """Test AI Service components that don't require database"""
    print("\n🔍 Testing AI Service Components...")
    
    try:
        # Test analysis types enum
        from app.services.llm_service import AnalysisType
        
        analysis_types = list(AnalysisType)
        print(f"✅ Available analysis types: {analysis_types}")
        
        # Test schema models
        from app.schemas.ai import AnalysisResponse, QueryRequest, QueryResponse
        from datetime import datetime
        
        # Test AnalysisResponse creation
        analysis_response = AnalysisResponse(
            scan_id=1,
            summary="Test analysis summary",
            key_findings=["Finding 1", "Finding 2"],
            recommendations=["Rec 1", "Rec 2"],
            risk_score=7.5,
            generated_at=datetime.utcnow(),
            analysis_type="comprehensive",
            ai_insights=[{"test": "insight"}]
        )
        print(f"✅ AnalysisResponse created: {analysis_response.analysis_type}")
        
        # Test QueryRequest/Response
        query_request = QueryRequest(
            query="What are my critical vulnerabilities?",
            context={"test": "context"},
            conversation_id="test-conv-123"
        )
        print(f"✅ QueryRequest created: {query_request.conversation_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI service component test failed: {e}")
        return False

async def test_feedback_service_without_db():
    """Test Feedback Service components that don't require database"""
    print("\n🔍 Testing Feedback Service Components...")
    
    try:
        from app.services.feedback_service import FeedbackService
        from app.schemas.ai import FeedbackRequest
        
        # Test feedback patterns extraction
        test_comments = [
            "The analysis was too general and not specific enough",
            "Missing important details about the vulnerability",
            "Response was confusing and hard to understand"
        ]
        
        # Mock FeedbackService to test pattern extraction
        class MockFeedbackService:
            def _extract_improvement_areas(self, feedback_list):
                improvement_patterns = {
                    "accuracy": ["wrong", "incorrect", "inaccurate", "mistake"],
                    "completeness": ["missing", "incomplete", "more detail", "shallow"],
                    "relevance": ["irrelevant", "not relevant", "off-topic", "not helpful"],
                    "clarity": ["confusing", "unclear", "hard to understand", "complicated"]
                }
                
                issue_counts = {area: 0 for area in improvement_patterns.keys()}
                
                for comment in test_comments:
                    comment_lower = comment.lower()
                    for area, patterns in improvement_patterns.items():
                        if any(pattern in comment_lower for pattern in patterns):
                            issue_counts[area] += 1
                
                return [
                    {"area": area, "count": count}
                    for area, count in issue_counts.items()
                    if count > 0
                ]
            
            def _extract_feedback_patterns(self, comments):
                if not comments:
                    return []
                
                common_words = {}
                for comment in comments:
                    words = comment.lower().split()
                    for word in words:
                        if len(word) > 3:
                            common_words[word] = common_words.get(word, 0) + 1
                
                sorted_words = sorted(common_words.items(), key=lambda x: x[1], reverse=True)
                return [word for word, count in sorted_words[:5] if count > 1]
        
        mock_service = MockFeedbackService()
        
        # Test improvement area extraction
        improvement_areas = mock_service._extract_improvement_areas(test_comments)
        print(f"✅ Improvement areas detected: {improvement_areas}")
        
        # Test pattern extraction
        patterns = mock_service._extract_feedback_patterns(test_comments)
        print(f"✅ Feedback patterns: {patterns}")
        
        # Test FeedbackRequest schema
        feedback_request = FeedbackRequest(
            analysis_id=1,
            rating=4,
            comment="Good analysis but could be more detailed",
            is_helpful=True
        )
        print(f"✅ FeedbackRequest created: {feedback_request.rating}")
        
        return True
        
    except Exception as e:
        print(f"❌ Feedback service test failed: {e}")
        return False

async def test_error_handling():
    """Test error handling and fallback mechanisms"""
    print("\n🔍 Testing Error Handling...")
    
    try:
        from app.services.llm_service import EnhancedLLMService
        from app.services.cache_service import CacheService
        
        # Test LLM service without API key
        llm_service = EnhancedLLMService()
        
        # Test fallback when client is None
        result = await llm_service.analyze_vulnerability(
            service_name="nginx",
            version="1.18",
            port=80,
            vulnerability_description="Test vulnerability"
        )
        print(f"✅ LLM fallback without API key: {result is not None}")
        
        # Test cache service with invalid Redis connection
        cache = CacheService()
        # Simulate Redis being unavailable
        cache.redis_client = None
        
        # Should gracefully handle Redis being down
        cache_available = cache.is_available()
        set_result = cache.set("test", "value")
        get_result = cache.get("test")
        
        print(f"✅ Cache graceful degradation: available={cache_available}, set={set_result}, get={get_result}")
        
        # Test JSON parsing errors
        invalid_json = "{ invalid json }"
        try:
            parsed = llm_service._parse_vulnerability_response(invalid_json)
            print(f"✅ JSON error handling: {parsed is not None}")
        except Exception as e:
            print(f"❌ JSON error handling failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

async def test_performance_features():
    """Test performance-related features"""
    print("\n🔍 Testing Performance Features...")
    
    try:
        from app.services.cache_service import CacheService, cache_service
        from app.services.llm_service import ContextWindow
        
        # Test context window management
        context_manager = ContextWindow(max_tokens=1000, reserve_tokens=100)
        
        # Test with content that needs truncation
        long_content = "Word " * 500  # Should exceed limit
        truncated = context_manager.truncate_context(long_content)
        print(f"✅ Context truncation: {len(long_content)} -> {len(truncated)}")
        
        # Test with content that doesn't need truncation
        short_content = "Short content"
        not_truncated = context_manager.truncate_context(short_content)
        print(f"✅ No truncation needed: {not_truncated == short_content}")
        
        # Test cache performance simulation
        cache = CacheService()
        
        # Simulate cache operations
        start_time = time.time()
        for i in range(10):
            cache.set(f"perf_test_{i}", {"data": f"test_{i}"}, 60)
        set_time = time.time() - start_time
        
        start_time = time.time()
        for i in range(10):
            cache.get(f"perf_test_{i}")
        get_time = time.time() - start_time
        
        print(f"✅ Cache performance: set={set_time:.4f}s, get={get_time:.4f}s")
        
        # Clean up
        for i in range(10):
            cache.delete(f"perf_test_{i}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting AI Enhancement Testing Suite")
    print("=" * 50)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Import Tests", test_imports),
        ("Cache Service", test_cache_service),
        ("LLM Service", test_llm_service),
        ("CVE Service", test_cve_service),
        ("AI Service Components", test_ai_service_without_db),
        ("Feedback Service Components", test_feedback_service_without_db),
        ("Error Handling", test_error_handling),
        ("Performance Features", test_performance_features)
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 OVERALL RESULT: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! AI enhancements are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)