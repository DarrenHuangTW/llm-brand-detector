"""增強的配置模型 - 支援模型選擇和詳細信息"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class StreamlitConfig(BaseModel):
    """Streamlit 應用配置"""
    max_competitors: int = 10
    max_prompts: int = 10

class ProviderInfo(BaseModel):
    """AI提供商增強信息"""
    name: str
    display_name: str
    models: List[str] = []
    default_model: str = ""
    model_descriptions: Dict[str, str] = {}

# 支援的 AI 提供商配置（2025年最新模型列表和定價）
SUPPORTED_PROVIDERS: Dict[str, ProviderInfo] = {
    "openai": ProviderInfo(
        name="openai",
        display_name="OpenAI",
        models=["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-5"],
        default_model="gpt-4o",
        model_descriptions={
            "gpt-4o": "\$2.50/\$10.00 per 1M tokens",
            "gpt-4o-mini": "\$0.15/\$0.60 per 1M tokens",
            "gpt-4.1": "\$2.00/\$8.00 per 1M tokens",
            "gpt-5": "\$1.25/\$10.00 per 1M tokens"
        }
    ),
    "anthropic": ProviderInfo(
        name="anthropic", 
        display_name="Anthropic",
        models=["claude-sonnet-4-0", "claude-3-7-sonnet-latest", "claude-3-5-haiku-20241022"],
        default_model="claude-sonnet-4-0",
        model_descriptions={
            "claude-sonnet-4-0": "\$3.00/\$15.00 per 1M tokens",
            "claude-3-7-sonnet-latest": "\$3.00/\$15.00 per 1M tokens",
            "claude-3-5-haiku-20241022": "\$0.80/\$4.00 per 1M tokens"
        }
    ),
    "google": ProviderInfo(
        name="google",
        display_name="Google", 
        models=["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"],
        default_model="gemini-2.5-flash",
        model_descriptions={
            "gemini-2.5-flash": "\$0.30/\$2.50 per 1M tokens",
            "gemini-2.5-flash-lite": "\$0.10/\$0.40 per 1M tokens",
            "gemini-2.5-pro": "\$1.25/\$10.00 per 1M tokens"
        }
    ),
    "perplexity": ProviderInfo(
        name="perplexity",
        display_name="Perplexity",
        models=["sonar", "sonar-pro"],
        default_model="sonar",
        model_descriptions={
            "sonar": "\$1.00/\$1.00 per 1M tokens + \$5/1K requests",
            "sonar-pro": "\$3.00/\$15.00 per 1M tokens + \$6/1K requests"
        }
    )
}

# 預設提示詞
DEFAULT_PROMPTS = [
    "What are the best project management tools for remote teams?",
    "Recommend top team collaboration platforms for startups", 
    "Which task management software is most popular among developers?",
    "Best agile project management tools for software development"
]