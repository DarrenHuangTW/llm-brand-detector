#!/usr/bin/env python3
"""重構驗證測試腳本"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """測試關鍵模組匯入"""
    print("Testing imports...")
    
    try:
        # 測試基本模型匯入
        from firegeo.models.analysis import SimpleAnalysisRequest, SimpleAnalysisResult
        print("✓ Models import successful")
        
        # 測試配置匯入
        from firegeo.models.config import StreamlitConfig, SUPPORTED_PROVIDERS
        print("✅ Config import successful")
        
        # 測試AI提供商匯入
        from firegeo.core.ai_providers import OpenAIProvider, AnthropicProvider, GoogleProvider, PerplexityProvider
        print("✅ AI Providers import successful")
        
        # 測試品牌檢測器匯入
        from firegeo.core.simple_detector import SimpleBrandDetector
        print("✅ Brand Detector import successful")
        
        # 測試工具匯入
        from firegeo.utils.api_validation import validate_api_keys
        from firegeo.utils.export import create_json_export, create_csv_export
        print("✅ Utilities import successful")
        
        # 測試主應用匯入
        from firegeo.streamlit_app import FireGEOStreamlitApp
        print("✅ Streamlit App import successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """測試基本功能"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # 測試配置創建
        from firegeo.models.config import StreamlitConfig, SUPPORTED_PROVIDERS
        config = StreamlitConfig()
        print(f"✅ Config created: max_competitors={config.max_competitors}")
        
        # 測試支援提供商
        print(f"✅ Supported providers: {list(SUPPORTED_PROVIDERS.keys())}")
        
        # 測試請求模型
        from firegeo.models.analysis import SimpleAnalysisRequest
        request = SimpleAnalysisRequest(
            target_brand="OpenAI",
            competitors=["Anthropic", "Google"],
            prompts=["What's the best AI company?"]
        )
        print("✅ Request model created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """主測試函數"""
    print("FireGEO Refactor Validation Test\n")
    
    # 測試匯入
    imports_ok = test_imports()
    
    # 測試基本功能
    functionality_ok = test_basic_functionality()
    
    # 總結
    print(f"\n📊 測試結果:")
    print(f"{'✅' if imports_ok else '❌'} 模組匯入")
    print(f"{'✅' if functionality_ok else '❌'} 基本功能")
    
    if imports_ok and functionality_ok:
        print("\n🎉 重構完成！應用已準備就緒")
        print("\n啟動命令:")
        print("uv run firegeo-streamlit")
        return 0
    else:
        print("\n⚠️ 發現問題，需要修復")
        return 1

if __name__ == "__main__":
    sys.exit(main())