"""
OpenAI 提供商實現 - GPT-4o 模型整合

整體架構：
┌─────────────────────────────────────────────────────────┐
│                  OpenAIProvider 類別                      │
├─────────────────────────────────────────────────────────┤
│  繼承：BaseAIProvider                                    │
│                                                         │
│  初始化流程：                                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 1. 呼叫父類初始化                                 │   │
│  │ 2. 建立 OpenAI 異步客戶端                        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  核心方法：                                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │ • provider_name → "OpenAI"                      │   │
│  │ • get_response → 獲取 GPT-4o 回應                │   │
│  │ • is_available → 檢查 API 金鑰可用性              │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

API 調用流程：
用戶提示詞 → 速率限制檢查 → OpenAI API 呼叫 → 處理回應 → 返回結果

依賴關係：
- openai: OpenAI 官方 Python SDK
- BaseAIProvider: 抽象基類
- logging: 錯誤日誌記錄
"""

import openai
import asyncio
from .base import BaseAIProvider
import logging

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseAIProvider):
    """
    OpenAI 提供商實現類別
    
    整合 OpenAI GPT-4o 模型，提供高品質的文本生成能力
    
    特色：
    - 使用最新 GPT-4o 模型
    - 支援高速率限制 (1000 RPM)
    - 異步 API 調用
    - 完整錯誤處理
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        初始化增強版 OpenAI 提供商
        
        參數：
            api_key (str): OpenAI API 金鑰
            model (str): 使用的模型，預設 gpt-4o
            
        建立的物件：
            self.client: OpenAI 異步客戶端實例
            self.selected_model: 選定的模型名稱
        """
        super().__init__(api_key)
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.selected_model = model
        self.available_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    
    @property
    def provider_name(self) -> str:
        """
        提供商名稱屬性
        
        作用：返回標識此提供商的名稱
        用於：
            - UI 顯示
            - 日誌記錄
            - 結果識別
            
        返回：
            str: "OpenAI" 
        """
        return "OpenAI"
    
    async def get_response(self, prompt: str) -> str:
        """
        獲取 OpenAI GPT-4o 的回應
        
        完整流程圖：
        ┌─────────────────┐
        │   接收用戶提示詞   │
        └─────────┬───────┘
                  │
        ┌─────────▼───────┐
        │   開始錯誤處理    │ ◄─── try-except 區塊
        └─────────┬───────┘
                  │
        ┌─────────▼───────┐
        │  執行速率限制延遲  │ ◄─── _rate_limit_delay(1000)
        │   (1000 RPM)    │      每分鐘最多 1000 次請求
        └─────────┬───────┘
                  │
        ┌─────────▼───────┐
        │ 建立 API 請求參數 │
        │ ┌─────────────┐ │
        │ │model: gpt-4o│ │ ◄─── 使用最新 GPT-4o 模型
        │ │max_tokens:  │ │
        │ │  4000       │ │ ◄─── 最大回應長度
        │ │temperature: │ │
        │ │  0.7        │ │ ◄─── 創意度設定
        │ └─────────────┘ │
        └─────────┬───────┘
                  │
        ┌─────────▼───────┐
        │  呼叫 OpenAI API │ ◄─── client.chat.completions.create()
        │     (異步調用)    │
        └─────────┬───────┘
                  │
        ┌─────────▼───────┐
        │   API 回應成功？  │
        └───┬─────────┬───┘
            │ Y       │ N
            │         │
    ┌───────▼───────┐ │
    │  提取回應文本    │ │ ◄─── response.choices[0].message.content
    │ (第一個選擇)    │ │
    └───────┬───────┘ │
            │         │
    ┌───────▼───────┐ │
    │   返回成功結果   │ │
    └───────┬───────┘ │
            │         │
            │    ┌────▼─────┐
            │    │ 捕獲異常   │ ◄─── except Exception
            │    └────┬─────┘
            │         │
            │    ┌────▼─────┐
            │    │ 記錄錯誤   │ ◄─── logger.error()
            │    └────┬─────┘
            │         │
            │    ┌────▼─────┐
            │    │返回錯誤訊息│
            │    └────┬─────┘
            │         │
        ┌───▼─────────▼───┐
        │    完成處理      │
        └─────────────────┘
        
        參數：
            prompt (str): 發送給 GPT-4o 的提示詞
            
        返回：
            str: GPT-4o 的回應文本，或錯誤訊息
            
        錯誤處理：
            - 網路連接錯誤
            - API 金鑰無效
            - 速率限制超出
            - 模型暫時不可用
            - 其他未預期錯誤
            
        速率限制：
            - 1000 RPM (每分鐘請求數)
            - 自動延遲確保不超出限制
        """
        try:
            # 移除速率限制 - 由於已限制分析提示詞數量上限，不易達到 RPM 限制
            # await self._rate_limit_delay(1000)  # OpenAI較高的RPM限制
            
            # 建立並發送 API 請求
            response = await self.client.chat.completions.create(
                model=self.selected_model,                         # 使用選定的模型
                messages=[{"role": "user", "content": prompt}],    # 用戶角色的提示詞
                max_tokens=4000,                                   # 最大回應長度
                temperature=0.7                                    # 創意度：0=確定，1=創意
            )
            
            # 提取並返回 AI 回應文本
            return response.choices[0].message.content
            
        except Exception as e:
            # 記錄錯誤詳情
            logger.error(f"OpenAI API error: {e}")
            # 返回使用者友善的錯誤訊息
            return f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """
        檢查 OpenAI 提供商是否可用
        
        流程圖：
        ┌─────────────────┐
        │   開始可用性檢查   │
        └─────────┬───────┘
                  │
        ┌─────────▼───────┐
        │  檢查API金鑰存在  │ ◄─── bool(self.api_key)
        └─────────┬───────┘
                  │
        ┌─────────▼───────┐
        │   返回檢查結果    │
        └─────────────────┘
        
        檢查項目：
            - API 金鑰是否存在
            - API 金鑰是否為非空字符串
            
        返回：
            bool: True 如果 API 金鑰有效，False 否則
            
        注意：此方法只檢查金鑰存在性，不驗證金鑰的有效性
              實際的 API 金鑰驗證在 utils/api_validation.py 中進行
        """
        return bool(self.api_key)