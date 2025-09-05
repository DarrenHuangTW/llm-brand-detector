"""簡化的品牌檢測系統 - 只使用Gemini 2.5 Flash"""

import asyncio
import json
import logging
from typing import Dict, List, Any
import google.generativeai as genai

from ..models.analysis import BrandDetectionResult

logger = logging.getLogger(__name__)

class SimpleBrandDetector:
    """極簡化的品牌檢測器"""
    
    def __init__(self, google_api_key: str):
        self.google_api_key = google_api_key
        self._configure_gemini()
    
    def _configure_gemini(self):
        """配置Gemini API"""
        genai.configure(api_key=self.google_api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    async def detect_single_brand(
        self, 
        text: str, 
        brand: str, 
        question: str
    ) -> BrandDetectionResult:
        """檢測單一品牌是否被提及"""
        
        prompt = f"""Please analyze if the brand '{brand}' is mentioned in the following AI response.

Consider the following when detecting brand mentions:
- Direct brand name mentions
- Product names clearly associated with the brand
- Company abbreviations or common variations
- Contextual references where the brand is clearly implied
- Ignore generic industry terms unless specifically referring to this brand

Original Question: {question}

AI Response: {text}

Response Requirements:
- Return only valid JSON format
- Use boolean value for brand_mentioned
- Provide brief reasoning for the decision

Expected JSON Format:
{{
  "brand_mentioned": true/false,
  "reasoning": "Brief explanation of detection logic"
}}"""

        try:
            response = await self._call_gemini(prompt)
            parsed_response = self._parse_json_response(response)
            
            return BrandDetectionResult(
                brand_name=brand,
                mentioned=parsed_response.get("brand_mentioned", False),
                reasoning=parsed_response.get("reasoning", "No reasoning provided")
            )
        except Exception as e:
            logger.error(f"Error detecting brand {brand}: {e}")
            return BrandDetectionResult(
                brand_name=brand,
                mentioned=False,
                reasoning=f"Detection error: {str(e)}"
            )
    
    async def detect_multiple_brands(
        self,
        text: str,
        target_brand: str,
        competitors: List[str],
        question: str
    ) -> Dict[str, BrandDetectionResult]:
        """使用單一 API 調用檢測多個品牌的提及情況"""
        
        all_brands = [target_brand] + competitors
        results = {}
        
        # 構建批量檢測提示詞
        brands_list = "\n".join([f"- {brand}" for brand in all_brands])
        
        batch_prompt = f"""Please analyze if any of the following brands are mentioned in the AI response below.

Brands to check:
{brands_list}

Consider the following when detecting brand mentions:
- Direct brand name mentions
- Product names clearly associated with the brand
- Company abbreviations or common variations
- Contextual references where the brand is clearly implied
- Ignore generic industry terms unless specifically referring to this brand

Original Question: {question}

AI Response: {text}

Response Requirements:
- Return only valid JSON format
- For each brand, provide a boolean value for mentioned
- Provide brief reasoning for each decision

Expected JSON Format:
{{
  "detections": [
    {{
      "brand_name": "Brand Name",
      "mentioned": true/false,
      "reasoning": "Brief explanation"
    }},
    ...
  ]
}}"""

        try:
            response = await self._call_gemini(batch_prompt)
            parsed_response = self._parse_json_response(response)
            
            # 處理批量檢測結果
            detections = parsed_response.get("detections", [])
            
            # 建立結果字典，確保所有品牌都有結果
            for brand in all_brands:
                results[brand] = BrandDetectionResult(
                    brand_name=brand,
                    mentioned=False,
                    reasoning="No detection result found"
                )
            
            # 更新實際檢測結果
            for detection in detections:
                brand_name = detection.get("brand_name", "")
                if brand_name in all_brands:
                    results[brand_name] = BrandDetectionResult(
                        brand_name=brand_name,
                        mentioned=detection.get("mentioned", False),
                        reasoning=detection.get("reasoning", "No reasoning provided")
                    )
            
        except Exception as e:
            logger.error(f"Error in batch brand detection: {e}")
            # 出錯時為所有品牌返回失敗結果
            for brand in all_brands:
                results[brand] = BrandDetectionResult(
                    brand_name=brand,
                    mentioned=False,
                    reasoning=f"Batch detection error: {str(e)}"
                )
        
        return results
    
    async def _call_gemini(self, prompt: str) -> str:
        """調用Gemini API"""
        loop = asyncio.get_event_loop()
        
        def _sync_call():
            response = self.model.generate_content(prompt)
            if not response.text:
                raise ValueError("Empty response from Gemini")
            return response.text.strip()
        
        return await asyncio.wait_for(
            loop.run_in_executor(None, _sync_call), 
            timeout=60.0
        )
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析JSON回應 - 支援單品牌和批量檢測格式"""
        try:
            # 嘗試直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 嘗試提取JSON區塊 - 改進的正則表達式
            import re
            
            # 尋找完整的JSON對象（支援嵌套）
            json_match = re.search(r'\{(?:[^{}]|{[^{}]*})*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # 嘗試尋找數組格式
            array_match = re.search(r'\[(?:[^\[\]]|\[[^\[\]]*\])*\]', response, re.DOTALL)
            if array_match:
                try:
                    array_data = json.loads(array_match.group())
                    # 如果找到數組，包裝成批量檢測格式
                    return {"detections": array_data}
                except json.JSONDecodeError:
                    pass
            
            # 嘗試從文本中提取結構化信息
            logger.warning(f"JSON parse failed, attempting fallback parsing. Response: {response[:200]}...")
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """當JSON解析失敗時的備用解析方法"""
        import re
        
        # 查找品牌提及的模式
        mentions = []
        
        # 常見的品牌名稱模式
        brand_patterns = [
            r'(\w+).*?mentioned.*?(true|false)',
            r'(\w+).*?(?:is|was).*?(mentioned|not mentioned|found|not found)',
            r'Brand.*?(\w+).*?(true|false|yes|no)',
        ]
        
        for pattern in brand_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                brand_name = match[0]
                mentioned = match[1].lower() in ['true', 'yes', 'mentioned', 'found']
                mentions.append({
                    "brand_name": brand_name,
                    "mentioned": mentioned,
                    "reasoning": f"Fallback parsing from: {match[0]} {match[1]}"
                })
        
        if mentions:
            return {"detections": mentions}
        
        # 完全失敗時返回空結果
        return {
            "detections": [],
            "parse_error": f"Failed to parse response: {response[:100]}..."
        }