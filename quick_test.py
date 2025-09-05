#!/usr/bin/env python3
"""Quick validation test"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("LLM Brand Detector Validation Test")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Models
    total_tests += 1
    try:
        from firegeo.models.analysis import SimpleAnalysisRequest
        print("+ Models import: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"- Models import: FAIL - {e}")
    
    # Test 2: AI Providers
    total_tests += 1
    try:
        from firegeo.core.ai_providers import OpenAIProvider
        print("+ AI Providers import: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"- AI Providers import: FAIL - {e}")
    
    # Test 3: Configuration (skip streamlit for now)
    total_tests += 1
    try:
        from firegeo.models.config import SUPPORTED_PROVIDERS
        providers = list(SUPPORTED_PROVIDERS.keys())
        assert len(providers) == 4  # OpenAI, Anthropic, Google, Perplexity
        assert "perplexity" in providers
        print("+ Configuration: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"- Configuration: FAIL - {e}")
    
    # Test 4: Brand Detector
    total_tests += 1
    try:
        from firegeo.core.simple_detector import SimpleBrandDetector
        print("+ Brand Detector: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"- Brand Detector: FAIL - {e}")
    
    print("\n" + "=" * 40)
    print(f"Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("SUCCESS: All tests passed!")
        print("\nTo run the application:")
        print("uv run firegeo-streamlit")
        return 0
    else:
        print("FAILURE: Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())