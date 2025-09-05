"""品牌檢測器單元測試"""

import pytest
import asyncio
from src.firegeo.core.brand_detector import BrandDetector
from src.firegeo.models.analysis import SentimentType


class TestBrandDetector:
    """品牌檢測器測試"""
    
    def test_normalize_brand_name(self, brand_detector: BrandDetector):
        """測試品牌名稱正規化"""
        # 基本正規化
        assert brand_detector.normalize_brand_name("  Test Brand  ") == "test brand"
        
        # 移除後綴
        assert brand_detector.normalize_brand_name("Test Company Inc") == "test"
        assert brand_detector.normalize_brand_name("Test Corp.") == "test"
        assert brand_detector.normalize_brand_name("Test Technologies") == "test"
        
        # 處理所有格
        assert brand_detector.normalize_brand_name("Test's Product") == "test product"
        
        # 處理空輸入
        assert brand_detector.normalize_brand_name("") == ""
        assert brand_detector.normalize_brand_name(None) == ""
    
    def test_generate_brand_variations(self, brand_detector: BrandDetector):
        """測試品牌變體生成"""
        variations = brand_detector.generate_brand_variations("Test Brand")
        
        # 基本檢查
        assert "test brand" in variations
        assert "testbrand" in variations
        assert "test-brand" in variations
        assert "test_brand" in variations
        assert "tb" in variations  # 首字母縮寫
        
        # 檢查長度過濾
        variations = brand_detector.generate_brand_variations("A")
        assert len([v for v in variations if len(v) < 2]) == 0
    
    def test_detect_sentiment_positive(self, brand_detector: BrandDetector):
        """測試正面情感檢測"""
        text = "This is the best project management tool. It's excellent and outstanding!"
        sentiment, confidence = brand_detector.detect_sentiment(text)
        
        assert sentiment == SentimentType.POSITIVE
        assert confidence > 0
    
    def test_detect_sentiment_negative(self, brand_detector: BrandDetector):
        """測試負面情感檢測"""
        text = "This tool is terrible and awful. It has many problems and limitations."
        sentiment, confidence = brand_detector.detect_sentiment(text)
        
        assert sentiment == SentimentType.NEGATIVE
        assert confidence > 0
    
    def test_detect_sentiment_neutral(self, brand_detector: BrandDetector):
        """測試中性情感檢測"""
        text = "This is a project management tool with various features."
        sentiment, confidence = brand_detector.detect_sentiment(text)
        
        assert sentiment == SentimentType.NEUTRAL
    
    def test_detect_sentiment_with_brand_context(self, brand_detector: BrandDetector):
        """測試帶品牌上下文的情感檢測"""
        text = "TestBrand is excellent for project management."
        sentiment, confidence = brand_detector.detect_sentiment(text, "TestBrand")
        
        assert sentiment == SentimentType.POSITIVE
        assert confidence > 0.5  # 品牌上下文應該提高信心
    
    def test_find_brand_position(self, brand_detector: BrandDetector):
        """測試品牌位置檢測"""
        # 明確排名
        text = "1. TestBrand - Great tool\n2. CompetitorA - Good tool"
        position = brand_detector.find_brand_position(text, "TestBrand", ["CompetitorA"])
        assert position == 1
        
        # 序數詞排名
        text = "1st TestBrand, 2nd CompetitorA"
        position = brand_detector.find_brand_position(text, "TestBrand", ["CompetitorA"])
        assert position == 1
        
        # 沒有找到排名
        text = "TestBrand is mentioned but not ranked"
        position = brand_detector.find_brand_position(text, "TestBrand", [])
        assert position is None
    
    @pytest.mark.asyncio
    async def test_detect_brand_mention_found(self, brand_detector: BrandDetector):
        """測試品牌提及檢測 - 找到品牌"""
        text = "TestBrand is the best project management tool available."
        
        result = await brand_detector.detect_brand_mention(text, "TestBrand", [])
        
        assert result.brand_mentioned is True
        assert result.sentiment == SentimentType.POSITIVE
        assert result.confidence > 0
        assert "TestBrand" in result.reasoning or "testbrand" in result.reasoning.lower()
    
    @pytest.mark.asyncio
    async def test_detect_brand_mention_not_found(self, brand_detector: BrandDetector):
        """測試品牌提及檢測 - 未找到品牌"""
        text = "This is about other tools and platforms."
        
        result = await brand_detector.detect_brand_mention(text, "TestBrand", [])
        
        assert result.brand_mentioned is False
        assert result.confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_detect_brand_mention_with_position(self, brand_detector: BrandDetector):
        """測試品牌提及檢測 - 包含位置"""
        text = "Top project management tools:\n1. TestBrand - excellent\n2. CompetitorA - good"
        
        result = await brand_detector.detect_brand_mention(
            text, "TestBrand", ["CompetitorA"]
        )
        
        assert result.brand_mentioned is True
        assert result.brand_position == 1
        assert result.sentiment == SentimentType.POSITIVE
    
    @pytest.mark.asyncio
    async def test_detect_brand_mention_variations(self, brand_detector: BrandDetector):
        """測試品牌變體檢測"""
        # 測試無空格變體
        text = "testbrand is a great tool"
        result = await brand_detector.detect_brand_mention(text, "Test Brand", [])
        assert result.brand_mentioned is True
        
        # 測試連字符變體
        text = "test-brand works well"
        result = await brand_detector.detect_brand_mention(text, "Test Brand", [])
        assert result.brand_mentioned is True
    
    @pytest.mark.asyncio
    async def test_detect_multiple_brands(self, brand_detector: BrandDetector):
        """測試多品牌檢測"""
        text = "BrandA is excellent, BrandB is good, BrandC is okay"
        brands = ["BrandA", "BrandB", "BrandC", "BrandD"]
        
        results = await brand_detector.detect_multiple_brands(text, brands)
        
        assert len(results) == 4
        assert results["BrandA"].brand_mentioned is True
        assert results["BrandB"].brand_mentioned is True  
        assert results["BrandC"].brand_mentioned is True
        assert results["BrandD"].brand_mentioned is False
    
    def test_empty_inputs(self, brand_detector: BrandDetector):
        """測試空輸入處理"""
        # 空品牌名稱
        variations = brand_detector.generate_brand_variations("")
        assert len(variations) == 0
        
        # 空文本情感檢測
        sentiment, confidence = brand_detector.detect_sentiment("")
        assert sentiment == SentimentType.NEUTRAL
        assert confidence == 0.0
        
        # 空文本位置檢測
        position = brand_detector.find_brand_position("", "TestBrand", [])
        assert position is None
    
    @pytest.mark.asyncio
    async def test_detect_brand_mention_empty_inputs(self, brand_detector: BrandDetector):
        """測試品牌檢測空輸入"""
        # 空文本
        result = await brand_detector.detect_brand_mention("", "TestBrand", [])
        assert result.brand_mentioned is False
        
        # 空品牌名稱
        result = await brand_detector.detect_brand_mention("some text", "", [])
        assert result.brand_mentioned is False