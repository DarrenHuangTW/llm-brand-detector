"""PyTest 配置和共享 fixtures"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from typing import Generator, Dict, Any

from src.firegeo.models.analysis import BrandAnalysis, AnalysisRequest, AIResponse, BrandMention, SentimentType
from src.firegeo.models.config import FireGEOSettings
from src.firegeo.storage.json_storage import JSONStorage
from src.firegeo.core.brand_detector import BrandDetector
from datetime import datetime


@pytest.fixture(scope="session")
def event_loop():
    """創建測試會話的事件循環"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_data_dir() -> Generator[Path, None, None]:
    """創建臨時數據目錄"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_settings(temp_data_dir: Path) -> FireGEOSettings:
    """測試用設定"""
    return FireGEOSettings(
        data_dir=str(temp_data_dir),
        analyses_file="test-analyses.json",
        debug=True,
        log_level="DEBUG",
        # 設置假的 API Keys 以便測試
        openai_api_key="test-key",
        anthropic_api_key="test-key",
        google_generative_ai_api_key="test-key",
        perplexity_api_key="test-key"
    )


@pytest.fixture
def json_storage(temp_data_dir: Path) -> JSONStorage:
    """測試用 JSON 存儲"""
    return JSONStorage(data_dir=str(temp_data_dir), filename="test-analyses.json")


@pytest.fixture
def brand_detector() -> BrandDetector:
    """品牌檢測器實例"""
    return BrandDetector()


@pytest.fixture
def sample_analysis_request() -> AnalysisRequest:
    """示例分析請求"""
    return AnalysisRequest(
        brand_name="TestBrand",
        competitors=["Competitor1", "Competitor2"],
        prompts=["What is the best project management tool?", "Recommend productivity apps"],
        enable_web_search=False
    )


@pytest.fixture
def sample_ai_response() -> AIResponse:
    """示例 AI 回應"""
    return AIResponse(
        provider="OpenAI",
        model_name="gpt-4o",
        prompt="What is the best project management tool?",
        response="The best project management tools include TestBrand, which is excellent for team collaboration.",
        brand_detection=BrandMention(
            brand_mentioned=True,
            brand_position=1,
            sentiment=SentimentType.POSITIVE,
            confidence=0.9,
            reasoning="TestBrand mentioned positively"
        ),
        brand_mentioned=True,
        brand_position=1,
        sentiment=SentimentType.POSITIVE,
        confidence=0.9,
        processing_time=1.5
    )


@pytest.fixture
def sample_brand_analysis(sample_ai_response: AIResponse) -> BrandAnalysis:
    """示例品牌分析結果"""
    analysis = BrandAnalysis(
        id="test-analysis-123",
        brand_name="TestBrand",
        competitors=["Competitor1", "Competitor2"],
        prompts=["What is the best project management tool?"]
    )
    analysis.ai_responses = [sample_ai_response]
    return analysis


@pytest.fixture
def mock_analyses_data() -> List[Dict[str, Any]]:
    """模擬分析數據"""
    return [
        {
            "id": "analysis-1",
            "brand_name": "Brand1",
            "competitors": ["CompA", "CompB"],
            "prompts": ["test prompt"],
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-01T12:00:00",
            "ai_responses": [],
            "metrics": None,
            "competitor_rankings": []
        },
        {
            "id": "analysis-2", 
            "brand_name": "Brand2",
            "competitors": ["CompC", "CompD"],
            "prompts": ["another test"],
            "created_at": "2024-01-02T12:00:00",
            "updated_at": "2024-01-02T12:00:00",
            "ai_responses": [],
            "metrics": None,
            "competitor_rankings": []
        }
    ]


@pytest.fixture
async def populated_storage(json_storage: JSONStorage, sample_brand_analysis: BrandAnalysis) -> JSONStorage:
    """預先填入數據的存儲"""
    await json_storage.save_analysis(sample_brand_analysis)
    return json_storage