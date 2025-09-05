"""簡化的Anthropic提供商"""

import anthropic
from .base import BaseAIProvider
import logging

logger = logging.getLogger(__name__)

class AnthropicProvider(BaseAIProvider):
    """Anthropic 提供商實現"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        super().__init__(api_key)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.selected_model = model
        self.available_models = ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-opus-4-1-20250805", "claude-3-opus-20240229"]
    
    @property
    def provider_name(self) -> str:
        return "Anthropic"
    
    async def get_response(self, prompt: str) -> str:
        """獲取Anthropic回應"""
        try:
            # 移除速率限制 - 由於已限制分析提示詞數量上限，不易達到 RPM 限制
            # await self._rate_limit_delay(100)  # Anthropic較低的RPM限制
            
            response = await self.client.messages.create(
                model=self.selected_model,
                max_tokens=4000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """檢查Anthropic是否可用"""
        return bool(self.api_key)