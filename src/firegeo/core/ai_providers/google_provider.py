"""簡化的Google提供商"""

import google.generativeai as genai
import asyncio
from .base import BaseAIProvider
import logging

logger = logging.getLogger(__name__)

class GoogleProvider(BaseAIProvider):
    """Google 提供商實現"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        super().__init__(api_key)
        genai.configure(api_key=api_key)
        self.selected_model = model
        self.available_models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-pro"]
        self.model = genai.GenerativeModel(model)
    
    @property
    def provider_name(self) -> str:
        return "Google"
    
    async def get_response(self, prompt: str) -> str:
        """獲取Google回應"""
        try:
            logger.info(f"Google API: Calling Gemini model with prompt length: {len(prompt)}")
            # 移除速率限制 - 由於已限制分析提示詞數量上限，不易達到 RPM 限制
            # await self._rate_limit_delay(120)  # Google較中等的RPM限制
            
            # 異步執行同步的API調用
            loop = asyncio.get_event_loop()
            def _sync_call():
                response = self.model.generate_content(prompt)
                return response.text
            
            response_text = await loop.run_in_executor(None, _sync_call)
            logger.info(f"Google API: Successfully received response with length: {len(response_text) if response_text else 0}")
            return response_text or "Empty response"
        except Exception as e:
            logger.error(f"Google API error: {e}")
            return f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """檢查Google是否可用"""
        return bool(self.api_key)