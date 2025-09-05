"""簡化的Perplexity提供商"""

import httpx
import json
from .base import BaseAIProvider
import logging

logger = logging.getLogger(__name__)

class PerplexityProvider(BaseAIProvider):
    """Perplexity 提供商實現"""
    
    def __init__(self, api_key: str, model: str = "sonar"):
        super().__init__(api_key)
        self.base_url = "https://api.perplexity.ai"
        self.selected_model = model
        self.available_models = ["sonar", "sonar-pro"]
    
    @property
    def provider_name(self) -> str:
        return "Perplexity"
    
    async def get_response(self, prompt: str) -> str:
        """獲取Perplexity回應"""
        try:
            # 移除速率限制 - 由於已限制分析提示詞數量上限，不易達到 RPM 限制
            # await self._rate_limit_delay(50)  # Perplexity較低的RPM限制
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.selected_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4000,
                "temperature": 0.7
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"Error: HTTP {response.status_code}"
                    
        except Exception as e:
            logger.error(f"Perplexity API error: {e}")
            return f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """檢查Perplexity是否可用"""
        return bool(self.api_key)