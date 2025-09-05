"""核心分析器單元測試"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from typing import List, Dict, Any

from src.firegeo.core.analyzer import BrandAnalyzer
from src.firegeo.core.ai_providers.base import BaseAIProvider
from src.firegeo.models.analysis import AnalysisRequest, BrandAnalysis, AIResponse, BrandMention, SentimentType
from src.firegeo.models.config import FireGEOSettings


@pytest.fixture
def mock_ai_provider():
    """模擬 AI 提供商"""
    provider = AsyncMock(spec=BaseAIProvider)
    provider.provider_name = "MockProvider"
    provider.model_name = "mock-model"
    provider.is_available = True
    return provider


@pytest.fixture
def analyzer_with_mock_providers(mock_ai_provider):
    """帶有模擬提供商的分析器"""
    settings = FireGEOSettings(
        openai_api_key="test-key",
        anthropic_api_key="test-key",
        enable_openai=True,
        enable_anthropic=False,
        enable_google=False,
        enable_perplexity=False
    )
    
    analyzer = BrandAnalyzer(settings=settings)
    # 替換提供商為模擬
    analyzer.ai_providers = [mock_ai_provider]
    return analyzer


class TestBrandAnalyzer:
    """品牌分析器測試"""
    
    def test_init_with_default_settings(self):
        """測試預設設定初始化"""
        analyzer = BrandAnalyzer()
        assert analyzer.settings is not None
        assert analyzer.storage is not None
        assert analyzer.brand_detector is not None
        assert analyzer.metrics_calculator is not None
    
    def test_init_with_custom_settings(self):
        """測試自定義設定初始化"""
        settings = FireGEOSettings(debug=True, log_level="DEBUG")
        analyzer = BrandAnalyzer(settings=settings)
        assert analyzer.settings.debug is True
        assert analyzer.settings.log_level == "DEBUG"
    
    def test_get_available_providers(self, analyzer_with_mock_providers, mock_ai_provider):
        """測試獲取可用提供商"""
        mock_ai_provider.is_available = True
        providers = analyzer_with_mock_providers._get_available_providers()
        assert len(providers) == 1
        assert providers[0] == mock_ai_provider
        
        # 測試不可用的提供商
        mock_ai_provider.is_available = False
        providers = analyzer_with_mock_providers._get_available_providers()
        assert len(providers) == 0
    
    @pytest.mark.asyncio
    async def test_query_single_provider_success(self, analyzer_with_mock_providers, mock_ai_provider):
        """測試單個提供商查詢成功"""
        # 設定模擬返回
        mock_response = AIResponse(
            provider="MockProvider",
            model_name="mock-model",
            prompt="test prompt",
            response="TestBrand is excellent for project management.",
            brand_detection=BrandMention(
                brand_mentioned=True,
                brand_position=1,
                sentiment=SentimentType.POSITIVE,
                confidence=0.9,
                reasoning="Positive mention found"
            ),
            brand_mentioned=True,
            brand_position=1,
            sentiment=SentimentType.POSITIVE,
            confidence=0.9,
            processing_time=1.0
        )
        mock_ai_provider.query.return_value = mock_response
        
        result = await analyzer_with_mock_providers._query_single_provider(
            mock_ai_provider, "test prompt", "TestBrand", []
        )
        
        assert result == mock_response
        mock_ai_provider.query.assert_called_once_with("test prompt", "TestBrand", [])
    
    @pytest.mark.asyncio
    async def test_query_single_provider_failure(self, analyzer_with_mock_providers, mock_ai_provider):
        """測試單個提供商查詢失敗"""
        mock_ai_provider.query.side_effect = Exception("API Error")
        
        result = await analyzer_with_mock_providers._query_single_provider(
            mock_ai_provider, "test prompt", "TestBrand", []
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_query_providers_success(self, analyzer_with_mock_providers, mock_ai_provider):
        """測試多提供商查詢成功"""
        mock_response = AIResponse(
            provider="MockProvider",
            model_name="mock-model",
            prompt="test prompt",
            response="TestBrand is great!",
            brand_detection=BrandMention(
                brand_mentioned=True,
                brand_position=None,
                sentiment=SentimentType.POSITIVE,
                confidence=0.8,
                reasoning="Found positive mention"
            ),
            brand_mentioned=True,
            brand_position=None,
            sentiment=SentimentType.POSITIVE,
            confidence=0.8,
            processing_time=0.5
        )
        mock_ai_provider.query.return_value = mock_response
        mock_ai_provider.is_available = True
        
        responses = await analyzer_with_mock_providers._query_providers(
            "test prompt", "TestBrand", []
        )
        
        assert len(responses) == 1
        assert responses[0] == mock_response
    
    @pytest.mark.asyncio
    async def test_query_providers_no_available(self, analyzer_with_mock_providers, mock_ai_provider):
        """測試沒有可用提供商"""
        mock_ai_provider.is_available = False
        
        responses = await analyzer_with_mock_providers._query_providers(
            "test prompt", "TestBrand", []
        )
        
        assert responses == []
    
    @pytest.mark.asyncio
    async def test_process_prompts(self, analyzer_with_mock_providers, mock_ai_provider):
        """測試處理多個提示詞"""
        mock_response1 = AIResponse(
            provider="MockProvider", model_name="mock-model",
            prompt="prompt1", response="TestBrand is good",
            brand_detection=BrandMention(
                brand_mentioned=True, sentiment=SentimentType.POSITIVE,
                confidence=0.8, reasoning="Found brand"
            ),
            brand_mentioned=True, sentiment=SentimentType.POSITIVE,
            confidence=0.8, processing_time=1.0
        )
        
        mock_response2 = AIResponse(
            provider="MockProvider", model_name="mock-model",
            prompt="prompt2", response="TestBrand is excellent",
            brand_detection=BrandMention(
                brand_mentioned=True, sentiment=SentimentType.POSITIVE,
                confidence=0.9, reasoning="Strong positive mention"
            ),
            brand_mentioned=True, sentiment=SentimentType.POSITIVE,
            confidence=0.9, processing_time=1.2
        )
        
        mock_ai_provider.query.side_effect = [mock_response1, mock_response2]
        mock_ai_provider.is_available = True
        
        all_responses = await analyzer_with_mock_providers._process_prompts(
            ["prompt1", "prompt2"], "TestBrand", [], None
        )
        
        assert len(all_responses) == 2
        assert all_responses[0] == mock_response1
        assert all_responses[1] == mock_response2
    
    @pytest.mark.asyncio
    async def test_analyze_brand_complete_flow(self, analyzer_with_mock_providers, mock_ai_provider, sample_analysis_request):
        """測試完整品牌分析流程"""
        # 設定模擬響應
        mock_response = AIResponse(
            provider="MockProvider", model_name="mock-model",
            prompt=sample_analysis_request.prompts[0],
            response="TestBrand is the best project management tool",
            brand_detection=BrandMention(
                brand_mentioned=True, brand_position=1,
                sentiment=SentimentType.POSITIVE, confidence=0.9,
                reasoning="Brand mentioned positively in first position"
            ),
            brand_mentioned=True, brand_position=1,
            sentiment=SentimentType.POSITIVE, confidence=0.9,
            processing_time=1.5
        )
        mock_ai_provider.query.return_value = mock_response
        mock_ai_provider.is_available = True
        
        # 模擬存儲保存
        with patch.object(analyzer_with_mock_providers.storage, 'save_analysis') as mock_save:
            mock_save.return_value = None
            
            analysis = await analyzer_with_mock_providers.analyze_brand(sample_analysis_request)
            
            # 驗證分析結果
            assert analysis.brand_name == "TestBrand"
            assert len(analysis.ai_responses) == 2  # 2個提示詞，每個1個響應
            assert analysis.metrics is not None
            assert analysis.metrics.visibility_score > 0
            
            # 驗證保存被調用
            mock_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_brand_with_progress_callback(self, analyzer_with_mock_providers, mock_ai_provider, sample_analysis_request):
        """測試帶進度回調的品牌分析"""
        progress_calls = []
        
        def progress_callback(current: int, total: int, message: str):
            progress_calls.append((current, total, message))
        
        mock_response = AIResponse(
            provider="MockProvider", model_name="mock-model",
            prompt="test", response="TestBrand works well",
            brand_detection=BrandMention(
                brand_mentioned=True, sentiment=SentimentType.POSITIVE,
                confidence=0.8, reasoning="Found brand"
            ),
            brand_mentioned=True, sentiment=SentimentType.POSITIVE,
            confidence=0.8, processing_time=1.0
        )
        mock_ai_provider.query.return_value = mock_response
        mock_ai_provider.is_available = True
        
        with patch.object(analyzer_with_mock_providers.storage, 'save_analysis'):
            analysis = await analyzer_with_mock_providers.analyze_brand(
                sample_analysis_request, progress_callback=progress_callback
            )
            
            # 驗證進度回調被調用
            assert len(progress_calls) > 0
            assert any("開始分析" in call[2] for call in progress_calls)
    
    @pytest.mark.asyncio
    async def test_analyze_brand_no_responses(self, analyzer_with_mock_providers, mock_ai_provider, sample_analysis_request):
        """測試沒有有效響應的情況"""
        mock_ai_provider.is_available = False  # 沒有可用提供商
        
        with patch.object(analyzer_with_mock_providers.storage, 'save_analysis'):
            analysis = await analyzer_with_mock_providers.analyze_brand(sample_analysis_request)
            
            # 應該仍然創建分析，但沒有響應和指標
            assert analysis.brand_name == "TestBrand"
            assert len(analysis.ai_responses) == 0
            assert analysis.metrics is not None
            assert analysis.metrics.visibility_score == 0
    
    @pytest.mark.asyncio
    async def test_get_analysis(self, analyzer_with_mock_providers):
        """測試獲取分析結果"""
        # 模擬存儲返回
        mock_analysis = BrandAnalysis(
            id="test-123", brand_name="TestBrand",
            competitors=[], prompts=["test"]
        )
        
        with patch.object(analyzer_with_mock_providers.storage, 'get_analysis', return_value=mock_analysis):
            result = await analyzer_with_mock_providers.get_analysis("test-123")
            assert result == mock_analysis
    
    @pytest.mark.asyncio
    async def test_list_analyses(self, analyzer_with_mock_providers):
        """測試列出分析結果"""
        mock_analyses = [
            BrandAnalysis(id="1", brand_name="Brand1", competitors=[], prompts=["test"]),
            BrandAnalysis(id="2", brand_name="Brand2", competitors=[], prompts=["test"])
        ]
        
        with patch.object(analyzer_with_mock_providers.storage, 'list_analyses', return_value=mock_analyses):
            results = await analyzer_with_mock_providers.list_analyses()
            assert len(results) == 2
            assert results == mock_analyses
    
    @pytest.mark.asyncio
    async def test_delete_analysis(self, analyzer_with_mock_providers):
        """測試刪除分析"""
        with patch.object(analyzer_with_mock_providers.storage, 'delete_analysis', return_value=True):
            result = await analyzer_with_mock_providers.delete_analysis("test-123")
            assert result is True
    
    @pytest.mark.asyncio
    async def test_export_analysis_json(self, analyzer_with_mock_providers):
        """測試 JSON 格式匯出"""
        mock_analysis = BrandAnalysis(
            id="test-123", brand_name="TestBrand",
            competitors=["Competitor1"], prompts=["test prompt"]
        )
        
        with patch.object(analyzer_with_mock_providers.storage, 'get_analysis', return_value=mock_analysis):
            result = await analyzer_with_mock_providers.export_analysis("test-123", "json")
            
            assert "TestBrand" in result
            assert "Competitor1" in result
            assert "test prompt" in result
    
    @pytest.mark.asyncio
    async def test_export_analysis_csv(self, analyzer_with_mock_providers):
        """測試 CSV 格式匯出"""
        mock_analysis = BrandAnalysis(
            id="test-123", brand_name="TestBrand",
            competitors=["Competitor1"], prompts=["test prompt"]
        )
        # 添加一些 AI 響應
        mock_analysis.ai_responses = [
            AIResponse(
                provider="Test", model_name="test-model",
                prompt="test", response="TestBrand is good",
                brand_detection=BrandMention(
                    brand_mentioned=True, sentiment=SentimentType.POSITIVE,
                    confidence=0.8, reasoning="Found brand"
                ),
                brand_mentioned=True, sentiment=SentimentType.POSITIVE,
                confidence=0.8, processing_time=1.0
            )
        ]
        
        with patch.object(analyzer_with_mock_providers.storage, 'get_analysis', return_value=mock_analysis):
            result = await analyzer_with_mock_providers.export_analysis("test-123", "csv")
            
            # CSV 應該包含標題行和數據行
            lines = result.strip().split('\n')
            assert len(lines) >= 2  # 至少標題和一行數據
            assert "Provider" in lines[0]  # 檢查標題
    
    @pytest.mark.asyncio
    async def test_export_analysis_not_found(self, analyzer_with_mock_providers):
        """測試匯出不存在的分析"""
        with patch.object(analyzer_with_mock_providers.storage, 'get_analysis', return_value=None):
            result = await analyzer_with_mock_providers.export_analysis("nonexistent", "json")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_storage_stats(self, analyzer_with_mock_providers):
        """測試獲取存儲統計"""
        mock_stats = {
            "total_analyses": 5,
            "file_size_bytes": 1024,
            "brands": ["Brand1", "Brand2"],
            "last_modified": "2024-01-01T12:00:00"
        }
        
        with patch.object(analyzer_with_mock_providers.storage, 'get_storage_stats', return_value=mock_stats):
            stats = await analyzer_with_mock_providers.get_storage_stats()
            assert stats == mock_stats
    
    @pytest.mark.asyncio
    async def test_error_handling_provider_failure(self, analyzer_with_mock_providers, mock_ai_provider):
        """測試提供商失敗的錯誤處理"""
        # 模擬所有查詢都失敗
        mock_ai_provider.query.side_effect = Exception("Network error")
        mock_ai_provider.is_available = True
        
        request = AnalysisRequest(
            brand_name="TestBrand",
            competitors=[],
            prompts=["test prompt"]
        )
        
        with patch.object(analyzer_with_mock_providers.storage, 'save_analysis'):
            analysis = await analyzer_with_mock_providers.analyze_brand(request)
            
            # 分析應該完成，但沒有響應
            assert analysis.brand_name == "TestBrand"
            assert len(analysis.ai_responses) == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis(self, analyzer_with_mock_providers, mock_ai_provider):
        """測試並發分析"""
        mock_response = AIResponse(
            provider="MockProvider", model_name="mock-model",
            prompt="test", response="Brand is good",
            brand_detection=BrandMention(
                brand_mentioned=True, sentiment=SentimentType.POSITIVE,
                confidence=0.8, reasoning="Found brand"
            ),
            brand_mentioned=True, sentiment=SentimentType.POSITIVE,
            confidence=0.8, processing_time=1.0
        )
        mock_ai_provider.query.return_value = mock_response
        mock_ai_provider.is_available = True
        
        # 創建多個並發分析請求
        requests = [
            AnalysisRequest(brand_name=f"Brand{i}", competitors=[], prompts=["test"])
            for i in range(3)
        ]
        
        with patch.object(analyzer_with_mock_providers.storage, 'save_analysis'):
            tasks = [
                analyzer_with_mock_providers.analyze_brand(req)
                for req in requests
            ]
            analyses = await asyncio.gather(*tasks)
            
            assert len(analyses) == 3
            for i, analysis in enumerate(analyses):
                assert analysis.brand_name == f"Brand{i}"