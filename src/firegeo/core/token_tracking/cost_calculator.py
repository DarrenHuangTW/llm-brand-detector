"""成本計算器 - 計算各種 AI 模型的使用成本"""

from typing import Dict, Optional

class CostCalculator:
    """AI 模型成本計算器"""
    
    # 2025年最新API定價（每1M tokens的USD成本）
    PRICING = {
        # OpenAI 定價
        "gpt-4o": {"input": 2.5, "output": 10.0},  # $2.5/$10 per 1M tokens
        "gpt-4o-mini": {"input": 0.15, "output": 0.6},  # $0.15/$0.6 per 1M tokens
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},  # 估計價格
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},  # 估計價格
        
        # Anthropic 定價
        "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},  # $3/$15 per 1M tokens
        "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},  # 使用 Sonnet 4 定價
        "claude-opus-4-1-20250805": {"input": 15.0, "output": 75.0},  # $15/$75 per 1M tokens
        "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},  # 使用 Opus 4.1 定價
        
        # Google 定價
        "gemini-2.5-flash": {"input": 0.3, "output": 2.5},  # $0.30/$2.5 per 1M tokens（新統一定價）
        "gemini-2.5-flash-lite": {"input": 0.1, "output": 0.4},  # $0.10/$0.40 per 1M tokens
        "gemini-pro": {"input": 0.5, "output": 1.5},  # 估計價格
        
        # Perplexity 定價（特殊計費方式：包含搜尋費用）
        "sonar": {
            "input": 1.33, "output": 1.33,  # $1/750K tokens ≈ $1.33/1M tokens
            "search_cost": 5.0  # $5/1000 searches = $0.005 per search
        },
        "sonar-pro": {
            "input": 4.0, "output": 20.0,  # $3/750K tokens ≈ $4/1M, $15/750K ≈ $20/1M
            "search_cost": 5.0  # $5/1000 searches
        }
    }
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int, 
                      search_requests: int = 0) -> float:
        """
        計算模型使用成本
        
        Args:
            model: 模型名稱
            input_tokens: 輸入 token 數量
            output_tokens: 輸出 token 數量  
            search_requests: 搜尋請求次數（Perplexity 專用）
            
        Returns:
            總成本（美元）
        """
        pricing = self.PRICING.get(model, {"input": 0, "output": 0})
        
        # 基本 token 成本計算
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        token_cost = input_cost + output_cost
        
        # Perplexity 搜尋成本計算
        search_cost = 0
        if "sonar" in model.lower() and search_requests > 0:
            search_cost = (search_requests / 1000) * pricing.get("search_cost", 0)
        
        return token_cost + search_cost
    
    def get_model_info(self, model: str) -> Dict[str, str]:
        """獲取模型詳細信息"""
        model_info = {
            # OpenAI 模型
            "gpt-4o": {
                "display_name": "GPT-4o",
                "description": "最新旗艦模型，推理能力最強",
                "cost_tier": "Premium",
                "speed": "Medium",
                "context_window": "128K tokens"
            },
            "gpt-4o-mini": {
                "display_name": "GPT-4o Mini", 
                "description": "輕量版，速度快成本低",
                "cost_tier": "Budget",
                "speed": "Fast",
                "context_window": "128K tokens"
            },
            
            # Anthropic 模型
            "claude-sonnet-4-20250514": {
                "display_name": "Claude Sonnet 4",
                "description": "最新版，平衡的推理能力與效率",
                "cost_tier": "Premium",
                "speed": "Medium",
                "context_window": "1M tokens"
            },
            "claude-opus-4-1-20250805": {
                "display_name": "Claude Opus 4.1",
                "description": "最新版，最強推理能力",
                "cost_tier": "Ultra",
                "speed": "Slow",
                "context_window": "1M tokens"
            },
            
            # Google 模型
            "gemini-2.5-flash": {
                "display_name": "Gemini 2.5 Flash",
                "description": "快速回應，強大多模態能力",
                "cost_tier": "Standard",
                "speed": "Fast",
                "context_window": "1M tokens"
            },
            "gemini-2.5-flash-lite": {
                "display_name": "Gemini 2.5 Flash Lite",
                "description": "最經濟選擇，適合大量請求",
                "cost_tier": "Budget",
                "speed": "Very Fast",
                "context_window": "1M tokens"
            },
            
            # Perplexity 模型
            "sonar": {
                "display_name": "Perplexity Sonar",
                "description": "即時搜尋，輕量模型",
                "cost_tier": "Standard",
                "speed": "Medium",
                "context_window": "Variable",
                "special": "包含即時網路搜尋"
            },
            "sonar-pro": {
                "display_name": "Perplexity Sonar Pro",
                "description": "進階搜尋，更深度分析",
                "cost_tier": "Premium", 
                "speed": "Slow",
                "context_window": "Variable",
                "special": "包含深度網路搜尋"
            }
        }
        
        return model_info.get(model, {
            "display_name": model,
            "description": "模型資訊待更新",
            "cost_tier": "Unknown",
            "speed": "Unknown",
            "context_window": "Unknown"
        })