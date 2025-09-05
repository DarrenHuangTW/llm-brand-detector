"""增強的資料模型 - 支援模型選擇和成本追蹤"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EnhancedAnalysisRequest(BaseModel):
    """增強的分析請求 - 支援模型選擇"""
    target_brand: str
    competitors: List[str] = []
    prompts: List[str] = []
    api_keys: Dict[str, str] = {}  # AI提供商API金鑰
    selected_models: Dict[str, str] = {}  # 每個提供商選擇的模型

# 保持向後兼容
SimpleAnalysisRequest = EnhancedAnalysisRequest

class BrandDetectionResult(BaseModel):
    """品牌檢測結果 - 只包含布林值和推理"""
    brand_name: str
    mentioned: bool
    reasoning: str

class AIProviderResponse(BaseModel):
    """增強的AI提供商回應 - 包含模型和成本信息"""
    provider: str
    model: str  # 新增：使用的具體模型
    prompt: str
    response_text: str
    brand_detections: Dict[str, BrandDetectionResult] = {}
    token_usage: Optional['TokenUsage'] = None  # 新增：token 使用統計
    processing_time: float = 0.0
    error: Optional[str] = None

class PromptAnalysisResult(BaseModel):
    """單一提示詞的分析結果"""
    prompt: str
    prompt_index: int
    ai_responses: Dict[str, AIProviderResponse] = {}

class SimpleAnalysisResult(BaseModel):
    """簡化的分析結果"""
    request: SimpleAnalysisRequest
    results_by_prompt: List[PromptAnalysisResult] = []
    created_at: datetime = Field(default_factory=datetime.now)
    total_prompts: int = 0
    completed_prompts: int = 0
    analysis_duration: float = 0.0

class TokenUsage(BaseModel):
    """增強的Token 使用統計"""
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    search_requests: int = 0  # 新增：搜尋請求次數（Perplexity 用）
    cost_estimate: Optional[float] = None

class EnhancedAnalysisResult(BaseModel):
    """增強的分析結果 - 包含成本追蹤"""
    request: EnhancedAnalysisRequest
    results_by_prompt: List[PromptAnalysisResult] = []
    token_usage: List[TokenUsage] = []  # 新增：所有 token 使用記錄
    created_at: datetime = Field(default_factory=datetime.now)
    total_prompts: int = 0
    completed_prompts: int = 0
    analysis_duration: float = 0.0
    total_cost: float = 0.0  # 新增：總成本

# 保持向後兼容
SimpleAnalysisResult = EnhancedAnalysisResult