"""增強的配置模型 - 支援模型選擇和詳細信息"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class StreamlitConfig(BaseModel):
    """Streamlit 應用配置"""
    title: str = "FireGEO Brand Analysis"
    page_icon: str = "🔥"
    layout: str = "wide"
    max_competitors: int = 10
    max_prompts: int = 10

class ProviderInfo(BaseModel):
    """AI提供商增強信息"""
    name: str
    display_name: str
    models: List[str] = []
    default_model: str = ""
    model_descriptions: Dict[str, str] = {}
    special_features: List[str] = []

# 支援的 AI 提供商配置（2025年最新模型列表和定價）
SUPPORTED_PROVIDERS: Dict[str, ProviderInfo] = {
    "openai": ProviderInfo(
        name="openai",
        display_name="OpenAI",
        models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        default_model="gpt-4o",
        model_descriptions={
            "gpt-4o": "最新旗艦模型，推理能力最強 ($2.5/$10 per 1M tokens)",
            "gpt-4o-mini": "輕量版，速度快成本低 ($0.15/$0.6 per 1M tokens)",
            "gpt-4-turbo": "平衡版本，性價比高 ($10/$30 per 1M tokens)",
            "gpt-3.5-turbo": "經典模型，成本最低 ($0.5/$1.5 per 1M tokens)"
        }
    ),
    "anthropic": ProviderInfo(
        name="anthropic", 
        display_name="Anthropic",
        models=["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-opus-4-1-20250805", "claude-3-opus-20240229"],
        default_model="claude-sonnet-4-20250514",
        model_descriptions={
            "claude-sonnet-4-20250514": "最新 Claude Sonnet 4，平衡推理能力與效率 ($3/$15 per 1M tokens)",
            "claude-3-5-sonnet-20241022": "上一代 Sonnet 模型 ($3/$15 per 1M tokens)",
            "claude-opus-4-1-20250805": "最新 Claude Opus 4.1，最強推理能力 ($15/$75 per 1M tokens)",
            "claude-3-opus-20240229": "上一代 Opus 模型 ($15/$75 per 1M tokens)"
        }
    ),
    "google": ProviderInfo(
        name="google",
        display_name="Google", 
        models=["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-pro"],
        default_model="gemini-2.5-flash",
        model_descriptions={
            "gemini-2.5-flash": "快速回應，強大多模態 ($0.30/$2.5 per 1M tokens)",
            "gemini-2.5-flash-lite": "最經濟選擇，大量請求首選 ($0.10/$0.40 per 1M tokens)",
            "gemini-pro": "經典模型 ($0.5/$1.5 per 1M tokens)"
        }
    ),
    "perplexity": ProviderInfo(
        name="perplexity",
        display_name="Perplexity",
        models=["sonar", "sonar-pro"],
        default_model="sonar",
        model_descriptions={
            "sonar": "即時搜尋，輕量模型 ($1.33/$1.33 per 1M tokens + $0.005/search)",
            "sonar-pro": "深度搜尋，進階分析 ($4/$20 per 1M tokens + $0.005/search)"
        },
        special_features=["real_time_search", "citation_support", "web_grounding"]
    )
}

# 預設提示詞
DEFAULT_PROMPTS = [
    "What are the best project management tools?",
    "Recommend top team collaboration platforms", 
    "Which productivity app is most popular?",
    "Best customer support software for small business"
]