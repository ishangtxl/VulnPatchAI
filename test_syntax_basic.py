#!/usr/bin/env python3
"""
Basic syntax and structure validation for AI enhancements
Tests code structure, syntax, and basic logic without external dependencies
"""
import ast
import os
import sys

def test_python_syntax(file_path):
    """Test if a Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST to check syntax
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def test_file_structure():
    """Test that all required files exist and have valid Python syntax"""
    print("🔍 Testing File Structure and Syntax...")
    
    required_files = [
        'backend/app/services/llm_service.py',
        'backend/app/services/ai_service.py', 
        'backend/app/services/cache_service.py',
        'backend/app/services/feedback_service.py',
        'backend/app/services/cve_service.py',
        'backend/app/schemas/ai.py',
        'backend/app/api/v1/endpoints/ai.py',
        'backend/app/models/feedback.py'
    ]
    
    results = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            valid, error = test_python_syntax(file_path)
            if valid:
                print(f"✅ {file_path} - Valid syntax")
                results.append(True)
            else:
                print(f"❌ {file_path} - {error}")
                results.append(False)
        else:
            print(f"❌ {file_path} - File not found")
            results.append(False)
    
    return all(results)

def test_code_structure():
    """Test code structure and class definitions"""
    print("\n🔍 Testing Code Structure...")
    
    try:
        # Test LLM service structure
        with open('backend/app/services/llm_service.py', 'r') as f:
            content = f.read()
        
        # Check for key classes and methods
        required_patterns = [
            'class EnhancedLLMService',
            'async def analyze_vulnerability',
            'async def answer_query',
            'class AnalysisType',
            'class VulnerabilityAnalysis',
            '_structured_vulnerability_analysis',
            '_business_impact_analysis',
            '_patch_recommendation_analysis'
        ]
        
        missing = []
        for pattern in required_patterns:
            if pattern not in content:
                missing.append(pattern)
        
        if missing:
            print(f"❌ LLM Service missing: {missing}")
            return False
        else:
            print("✅ LLM Service structure complete")
        
        # Test cache service structure
        with open('backend/app/services/cache_service.py', 'r') as f:
            content = f.read()
        
        cache_patterns = [
            'class CacheService',
            'class CVECache', 
            'class AIResponseCache',
            'def set',
            'def get',
            'def delete'
        ]
        
        missing = []
        for pattern in cache_patterns:
            if pattern not in content:
                missing.append(pattern)
                
        if missing:
            print(f"❌ Cache Service missing: {missing}")
            return False
        else:
            print("✅ Cache Service structure complete")
        
        # Test AI service structure
        with open('backend/app/services/ai_service.py', 'r') as f:
            content = f.read()
        
        ai_patterns = [
            'class EnhancedAIService',
            'async def process_query',
            'async def analyze_scan',
            '_comprehensive_analysis',
            '_business_impact_analysis',
            '_patch_prioritization_analysis'
        ]
        
        missing = []
        for pattern in ai_patterns:
            if pattern not in content:
                missing.append(pattern)
                
        if missing:
            print(f"❌ AI Service missing: {missing}")
            return False
        else:
            print("✅ AI Service structure complete")
        
        return True
        
    except Exception as e:
        print(f"❌ Code structure test failed: {e}")
        return False

def test_schemas_and_models():
    """Test schema and model definitions"""
    print("\n🔍 Testing Schemas and Models...")
    
    try:
        # Test AI schemas
        with open('backend/app/schemas/ai.py', 'r') as f:
            content = f.read()
        
        schema_patterns = [
            'class QueryRequest',
            'class QueryResponse', 
            'class AnalysisRequest',
            'class AnalysisResponse',
            'class FeedbackRequest',
            'class VulnerabilityInsight',
            'class BusinessRiskAssessment'
        ]
        
        missing = []
        for pattern in schema_patterns:
            if pattern not in content:
                missing.append(pattern)
                
        if missing:
            print(f"❌ AI Schemas missing: {missing}")
            return False
        else:
            print("✅ AI Schemas complete")
        
        # Test enhanced feedback model
        with open('backend/app/models/feedback.py', 'r') as f:
            content = f.read()
        
        model_patterns = [
            'class Feedback',
            'analysis_id',
            'conversation_id',
            'feedback_data',
            'is_helpful'
        ]
        
        missing = []
        for pattern in model_patterns:
            if pattern not in content:
                missing.append(pattern)
                
        if missing:
            print(f"❌ Feedback Model missing: {missing}")
            return False
        else:
            print("✅ Feedback Model enhanced")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema/Model test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoint definitions"""
    print("\n🔍 Testing API Endpoints...")
    
    try:
        with open('backend/app/api/v1/endpoints/ai.py', 'r') as f:
            content = f.read()
        
        endpoint_patterns = [
            '@router.post("/query"',
            '@router.post("/analyze"',
            '@router.post("/analyze/business-impact"',
            '@router.post("/analyze/patch-prioritization"',
            '@router.post("/feedback"',
            '@router.get("/feedback/analytics"',
            '@router.get("/cache/stats"',
            '@router.get("/performance/metrics"',
            'async def ask_ai',
            'async def analyze_scan',
            'EnhancedAIService'
        ]
        
        missing = []
        for pattern in endpoint_patterns:
            if pattern not in content:
                missing.append(pattern)
                
        if missing:
            print(f"❌ API Endpoints missing: {missing}")
            return False
        else:
            print("✅ API Endpoints complete")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def test_requirements():
    """Test that requirements.txt has been updated"""
    print("\n🔍 Testing Requirements...")
    
    try:
        with open('backend/requirements.txt', 'r') as f:
            content = f.read()
        
        # Check for updated dependencies
        required_deps = [
            'openai==1.54.4',  # Updated OpenAI
            'redis==',         # Redis for caching
            'pydantic==',      # Pydantic models
        ]
        
        missing = []
        for dep in required_deps:
            if dep not in content:
                missing.append(dep)
        
        if missing:
            print(f"❌ Requirements missing: {missing}")
            return False
        else:
            print("✅ Requirements updated with new dependencies")
        
        return True
        
    except Exception as e:
        print(f"❌ Requirements test failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("🚀 Starting Basic AI Enhancement Validation")
    print("=" * 50)
    
    tests = [
        ("File Structure & Syntax", test_file_structure),
        ("Code Structure", test_code_structure),
        ("Schemas & Models", test_schemas_and_models),
        ("API Endpoints", test_api_endpoints),
        ("Requirements", test_requirements)
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
    print("📊 BASIC VALIDATION RESULTS")
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
        print("🎉 ALL BASIC TESTS PASSED! Code structure is correct.")
        print("📝 Next: Test with Docker environment for full functionality")
    else:
        print("⚠️  Some basic tests failed. Fix syntax/structure issues first.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)