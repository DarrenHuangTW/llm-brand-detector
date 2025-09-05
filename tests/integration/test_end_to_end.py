"""端到端集成測試"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch
import json

from src.firegeo.core.analyzer import BrandAnalyzer
from src.firegeo.models.analysis import AnalysisRequest, SentimentType, BrandMention, AIResponse
from src.firegeo.models.config import FireGEOSettings
from src.firegeo.storage.json_storage import JSONStorage


@pytest.fixture
def integration_settings(temp_data_dir: Path) -> FireGEOSettings:
    """集成測試設定"""
    return FireGEOSettings(
        data_dir=str(temp_data_dir),
        analyses_file="integration-test.json",
        debug=True,
        log_level="DEBUG",
        # 使用假 API Keys 進行測試
        openai_api_key="test-openai-key",
        anthropic_api_key="test-anthropic-key",
        google_generative_ai_api_key="test-google-key",
        perplexity_api_key="test-perplexity-key",
        # 只啟用一個提供商以簡化測試
        enable_openai=True,
        enable_anthropic=False,
        enable_google=False,
        enable_perplexity=False
    )


@pytest.fixture
def mock_openai_responses():
    """模擬 OpenAI 響應數據"""
    return [
        AIResponse(
            provider="OpenAI",
            model_name="gpt-4o",
            prompt="What is the best project management tool?",
            response="The best project management tools include TestBrand, which excels in team collaboration and task organization. It offers excellent features for tracking progress and managing deadlines.",
            brand_detection=BrandMention(
                brand_mentioned=True,
                brand_position=1,
                sentiment=SentimentType.POSITIVE,
                confidence=0.92,
                reasoning="TestBrand is mentioned first and described very positively with words like 'excels' and 'excellent'"
            ),
            brand_mentioned=True,
            brand_position=1,
            sentiment=SentimentType.POSITIVE,
            confidence=0.92,
            processing_time=1.5
        ),
        AIResponse(
            provider="OpenAI",
            model_name="gpt-4o",
            prompt="Recommend productivity apps",
            response="For productivity, I recommend several apps: 1. TestBrand for project management, 2. Notion for note-taking, 3. Competitor1 for time tracking. TestBrand stands out for its intuitive interface.",
            brand_detection=BrandMention(
                brand_mentioned=True,
                brand_position=1,
                sentiment=SentimentType.POSITIVE,
                confidence=0.88,
                reasoning="TestBrand mentioned in position 1 and praised for its intuitive interface"
            ),
            brand_mentioned=True,
            brand_position=1,
            sentiment=SentimentType.POSITIVE,
            confidence=0.88,
            processing_time=1.8
        )
    ]


class TestEndToEnd:
    """端到端集成測試"""
    
    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(self, integration_settings, mock_openai_responses):
        """測試完整的分析工作流程"""
        # 創建分析器
        analyzer = BrandAnalyzer(settings=integration_settings)
        
        # 模擬 OpenAI 提供商的響應
        with patch('src.firegeo.core.ai_providers.openai_provider.OpenAIProvider.query') as mock_query:
            mock_query.side_effect = mock_openai_responses
            
            # 創建分析請求
            request = AnalysisRequest(
                brand_name="TestBrand",
                competitors=["Competitor1", "Competitor2"],
                prompts=[
                    "What is the best project management tool?",
                    "Recommend productivity apps"
                ],
                enable_web_search=False
            )
            
            # 執行分析
            progress_updates = []
            def progress_callback(current: int, total: int, message: str):
                progress_updates.append((current, total, message))
            
            analysis = await analyzer.analyze_brand(request, progress_callback=progress_callback)
            
            # 驗證分析結果
            assert analysis is not None
            assert analysis.brand_name == "TestBrand"
            assert analysis.competitors == ["Competitor1", "Competitor2"]
            assert len(analysis.prompts) == 2
            assert len(analysis.ai_responses) == 2
            
            # 驗證 AI 響應
            for response in analysis.ai_responses:
                assert response.provider == "OpenAI"
                assert response.brand_mentioned is True
                assert response.sentiment == SentimentType.POSITIVE
                assert response.confidence > 0.8
            
            # 驗證指標計算
            assert analysis.metrics is not None
            assert analysis.metrics.visibility_score == 100.0  # 100% 提及率
            assert analysis.metrics.sentiment_score > 80  # 正面情感
            assert analysis.metrics.confidence_score > 0.8
            assert analysis.metrics.total_mentions == 2
            assert analysis.metrics.positive_mentions == 2
            
            # 驗證進度回調
            assert len(progress_updates) > 0
            assert any("開始分析" in update[2] for update in progress_updates)
            
            # 驗證數據已保存
            stored_analysis = await analyzer.get_analysis(analysis.id)
            assert stored_analysis is not None
            assert stored_analysis.brand_name == "TestBrand"
    
    @pytest.mark.asyncio
    async def test_analysis_with_mixed_sentiment(self, integration_settings):
        """測試混合情感的分析"""
        analyzer = BrandAnalyzer(settings=integration_settings)
        
        # 模擬包含正面和負面情感的響應
        mixed_responses = [
            AIResponse(
                provider="OpenAI", model_name="gpt-4o",
                prompt="What do you think about TestBrand?",
                response="TestBrand is excellent for small teams but has limitations for enterprise use. It's user-friendly but lacks advanced features.",
                brand_detection=BrandMention(
                    brand_mentioned=True, brand_position=None,
                    sentiment=SentimentType.NEUTRAL, confidence=0.75,
                    reasoning="Mixed sentiment - both positive and negative aspects mentioned"
                ),
                brand_mentioned=True, brand_position=None,
                sentiment=SentimentType.NEUTRAL, confidence=0.75,
                processing_time=1.2
            ),
            AIResponse(
                provider="OpenAI", model_name="gpt-4o",
                prompt="Any issues with TestBrand?",
                response="TestBrand has some problems with performance and customer support. Many users complain about slow response times.",
                brand_detection=BrandMention(
                    brand_mentioned=True, brand_position=None,
                    sentiment=SentimentType.NEGATIVE, confidence=0.85,
                    reasoning="Clearly negative mentions regarding problems, complaints, and poor performance"
                ),
                brand_mentioned=True, brand_position=None,
                sentiment=SentimentType.NEGATIVE, confidence=0.85,
                processing_time=1.1
            )
        ]
        
        with patch('src.firegeo.core.ai_providers.openai_provider.OpenAIProvider.query') as mock_query:
            mock_query.side_effect = mixed_responses
            
            request = AnalysisRequest(
                brand_name="TestBrand",
                competitors=[],
                prompts=["What do you think about TestBrand?", "Any issues with TestBrand?"]
            )
            
            analysis = await analyzer.analyze_brand(request)
            
            # 驗證混合情感分析
            assert analysis.metrics.total_mentions == 2
            assert analysis.metrics.positive_mentions == 0
            assert analysis.metrics.negative_mentions == 1
            assert analysis.metrics.neutral_mentions == 1
            assert 0 < analysis.metrics.sentiment_score < 80  # 中等情感分數
    
    @pytest.mark.asyncio
    async def test_brand_not_mentioned(self, integration_settings):
        """測試品牌未被提及的情況"""
        analyzer = BrandAnalyzer(settings=integration_settings)
        
        # 模擬不提及目標品牌的響應
        no_mention_responses = [
            AIResponse(
                provider="OpenAI", model_name="gpt-4o",
                prompt="What are the best productivity tools?",
                response="The best productivity tools include Notion for note-taking, Slack for communication, and Trello for task management. These tools help teams stay organized.",
                brand_detection=BrandMention(
                    brand_mentioned=False, brand_position=None,
                    sentiment=SentimentType.NEUTRAL, confidence=0.0,
                    reasoning="TestBrand is not mentioned in the response"
                ),
                brand_mentioned=False, brand_position=None,
                sentiment=SentimentType.NEUTRAL, confidence=0.0,
                processing_time=1.0
            )
        ]
        
        with patch('src.firegeo.core.ai_providers.openai_provider.OpenAIProvider.query') as mock_query:
            mock_query.side_effect = no_mention_responses
            
            request = AnalysisRequest(
                brand_name="TestBrand",
                competitors=[],
                prompts=["What are the best productivity tools?"]
            )
            
            analysis = await analyzer.analyze_brand(request)
            
            # 驗證無提及情況
            assert analysis.metrics.visibility_score == 0.0
            assert analysis.metrics.total_mentions == 0
            assert analysis.metrics.market_share == 0.0
    
    @pytest.mark.asyncio
    async def test_competitor_ranking_analysis(self, integration_settings):
        """測試競爭對手排名分析"""
        analyzer = BrandAnalyzer(settings=integration_settings)
        
        # 模擬包含排名的響應
        ranking_responses = [
            AIResponse(
                provider="OpenAI", model_name="gpt-4o",
                prompt="Rank the top project management tools",
                response="Top project management tools: 1. Competitor1 - excellent features, 2. TestBrand - good for small teams, 3. Competitor2 - basic but reliable.",
                brand_detection=BrandMention(
                    brand_mentioned=True, brand_position=2,
                    sentiment=SentimentType.POSITIVE, confidence=0.8,
                    reasoning="TestBrand mentioned in position 2 with positive description"
                ),
                brand_mentioned=True, brand_position=2,
                sentiment=SentimentType.POSITIVE, confidence=0.8,
                processing_time=1.3
            )
        ]
        
        with patch('src.firegeo.core.ai_providers.openai_provider.OpenAIProvider.query') as mock_query:
            mock_query.side_effect = ranking_responses
            
            request = AnalysisRequest(
                brand_name="TestBrand",
                competitors=["Competitor1", "Competitor2"],
                prompts=["Rank the top project management tools"]
            )
            
            analysis = await analyzer.analyze_brand(request)
            
            # 驗證排名分析
            assert len(analysis.competitor_rankings) > 0
            testbrand_ranking = next((r for r in analysis.competitor_rankings if r.brand == "TestBrand"), None)
            assert testbrand_ranking is not None
            assert testbrand_ranking.average_position == 2.0
    
    @pytest.mark.asyncio
    async def test_export_and_import_workflow(self, integration_settings, mock_openai_responses):
        """測試匯出和匯入工作流程"""
        analyzer = BrandAnalyzer(settings=integration_settings)
        
        with patch('src.firegeo.core.ai_providers.openai_provider.OpenAIProvider.query') as mock_query:
            mock_query.side_effect = mock_openai_responses
            
            # 執行分析
            request = AnalysisRequest(
                brand_name="TestBrand",
                competitors=["Competitor1"],
                prompts=["Test prompt"]
            )
            
            analysis = await analyzer.analyze_brand(request)
            analysis_id = analysis.id
            
            # 測試 JSON 匯出
            json_export = await analyzer.export_analysis(analysis_id, "json")
            assert json_export is not None
            exported_data = json.loads(json_export)
            assert exported_data["brand_name"] == "TestBrand"
            
            # 測試 CSV 匯出
            csv_export = await analyzer.export_analysis(analysis_id, "csv")
            assert csv_export is not None
            csv_lines = csv_export.strip().split('\n')
            assert len(csv_lines) >= 2  # 標題行 + 至少一行數據
            
            # 測試存儲統計
            stats = await analyzer.get_storage_stats()
            assert stats["total_analyses"] >= 1
            assert "TestBrand" in stats["brands"]
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, integration_settings):
        """測試錯誤恢復工作流程"""
        analyzer = BrandAnalyzer(settings=integration_settings)
        
        # 模擬部分失敗的情況（一個成功，一個失敗）
        def side_effect(*args, **kwargs):
            if "first prompt" in args[0]:
                return AIResponse(
                    provider="OpenAI", model_name="gpt-4o",
                    prompt="first prompt", response="TestBrand is good",
                    brand_detection=BrandMention(
                        brand_mentioned=True, sentiment=SentimentType.POSITIVE,
                        confidence=0.8, reasoning="Found brand"
                    ),
                    brand_mentioned=True, sentiment=SentimentType.POSITIVE,
                    confidence=0.8, processing_time=1.0
                )
            else:
                raise Exception("API Error")
        
        with patch('src.firegeo.core.ai_providers.openai_provider.OpenAIProvider.query') as mock_query:
            mock_query.side_effect = side_effect
            
            request = AnalysisRequest(
                brand_name="TestBrand",
                competitors=[],
                prompts=["first prompt", "second prompt that will fail"]
            )
            
            # 分析應該部分成功
            analysis = await analyzer.analyze_brand(request)
            
            # 驗證錯誤恢復
            assert analysis is not None
            assert len(analysis.ai_responses) == 1  # 只有成功的響應
            assert analysis.metrics.visibility_score == 100.0  # 基於可用數據
    
    @pytest.mark.asyncio
    async def test_concurrent_analyses(self, integration_settings):
        """測試並發分析"""
        analyzer = BrandAnalyzer(settings=integration_settings)
        
        # 模擬響應
        def create_response(brand_name: str, prompt: str):
            return AIResponse(
                provider="OpenAI", model_name="gpt-4o",
                prompt=prompt, response=f"{brand_name} is a great tool",
                brand_detection=BrandMention(
                    brand_mentioned=True, sentiment=SentimentType.POSITIVE,
                    confidence=0.8, reasoning=f"Found {brand_name}"
                ),
                brand_mentioned=True, sentiment=SentimentType.POSITIVE,
                confidence=0.8, processing_time=1.0
            )
        
        with patch('src.firegeo.core.ai_providers.openai_provider.OpenAIProvider.query') as mock_query:
            # 為每個品牌創建不同的響應
            responses = []
            for i in range(3):
                responses.append(create_response(f"Brand{i}", f"prompt{i}"))
            mock_query.side_effect = responses
            
            # 創建並發分析請求
            requests = [
                AnalysisRequest(
                    brand_name=f"Brand{i}",
                    competitors=[],
                    prompts=[f"prompt{i}"]
                )
                for i in range(3)
            ]
            
            # 並發執行分析
            tasks = [analyzer.analyze_brand(req) for req in requests]
            analyses = await asyncio.gather(*tasks)
            
            # 驗證並發結果
            assert len(analyses) == 3
            for i, analysis in enumerate(analyses):
                assert analysis.brand_name == f"Brand{i}"
                assert len(analysis.ai_responses) == 1
            
            # 驗證所有分析都已保存
            all_analyses = await analyzer.list_analyses()
            assert len(all_analyses) >= 3
    
    @pytest.mark.asyncio
    async def test_storage_persistence(self, integration_settings):
        """測試數據持久化"""
        # 創建第一個分析器實例
        analyzer1 = BrandAnalyzer(settings=integration_settings)
        
        with patch('src.firegeo.core.ai_providers.openai_provider.OpenAIProvider.query') as mock_query:
            mock_query.return_value = AIResponse(
                provider="OpenAI", model_name="gpt-4o",
                prompt="test", response="TestBrand works well",
                brand_detection=BrandMention(
                    brand_mentioned=True, sentiment=SentimentType.POSITIVE,
                    confidence=0.8, reasoning="Found brand"
                ),
                brand_mentioned=True, sentiment=SentimentType.POSITIVE,
                confidence=0.8, processing_time=1.0
            )
            
            # 執行分析
            request = AnalysisRequest(
                brand_name="PersistenceBrand",
                competitors=[],
                prompts=["test prompt"]
            )
            
            analysis = await analyzer1.analyze_brand(request)
            analysis_id = analysis.id
            
            # 創建第二個分析器實例（模擬重啟應用）
            analyzer2 = BrandAnalyzer(settings=integration_settings)
            
            # 驗證數據仍然存在
            retrieved_analysis = await analyzer2.get_analysis(analysis_id)
            assert retrieved_analysis is not None
            assert retrieved_analysis.brand_name == "PersistenceBrand"
            
            # 驗證列表功能
            all_analyses = await analyzer2.list_analyses()
            assert any(a.brand_name == "PersistenceBrand" for a in all_analyses)