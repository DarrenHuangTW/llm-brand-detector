"""Token 使用追蹤器 - 記錄和統計 API 調用的 Token 用量"""

from typing import List, Optional
from .cost_calculator import CostCalculator
from ...models.analysis import TokenUsage

class TokenTracker:
    """Token 使用量追蹤器"""
    
    def __init__(self):
        self.usage_history: List[TokenUsage] = []
        self.cost_calculator = CostCalculator()
    
    def track_usage(self, provider: str, model: str, 
                   prompt_tokens: int, completion_tokens: int,
                   search_requests: int = 0) -> TokenUsage:
        """
        記錄 Token 使用量
        
        Args:
            provider: AI 提供商名稱
            model: 模型名稱
            prompt_tokens: 輸入 token 數量
            completion_tokens: 輸出 token 數量
            search_requests: 搜尋請求次數（Perplexity 用）
            
        Returns:
            TokenUsage 對象
        """
        usage = TokenUsage(
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            search_requests=search_requests,
            cost_estimate=self.cost_calculator.calculate_cost(
                model, prompt_tokens, completion_tokens, search_requests
            )
        )
        
        self.usage_history.append(usage)
        return usage
    
    def get_total_cost(self) -> float:
        """獲取總成本"""
        return sum(usage.cost_estimate or 0 for usage in self.usage_history)
    
    def get_total_tokens(self) -> int:
        """獲取總 token 數量"""
        return sum(usage.total_tokens for usage in self.usage_history)
    
    def get_usage_by_provider(self) -> dict:
        """按提供商統計使用量"""
        provider_stats = {}
        for usage in self.usage_history:
            if usage.provider not in provider_stats:
                provider_stats[usage.provider] = {
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "calls": 0
                }
            
            provider_stats[usage.provider]["total_tokens"] += usage.total_tokens
            provider_stats[usage.provider]["total_cost"] += (usage.cost_estimate or 0)
            provider_stats[usage.provider]["calls"] += 1
        
        return provider_stats
    
    def clear_history(self):
        """清除使用歷史"""
        self.usage_history.clear()