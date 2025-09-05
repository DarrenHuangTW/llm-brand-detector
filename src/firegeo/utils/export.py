"""匯出功能模組"""

import json
import csv
import io
from datetime import datetime
from typing import List, Dict, Any
from ..models.analysis import SimpleAnalysisResult

def create_json_export(result: SimpleAnalysisResult) -> str:
    """創建JSON格式的匯出數據"""
    
    export_data = {
        "analysis_summary": {
            "target_brand": result.request.target_brand,
            "competitors": result.request.competitors,
            "total_prompts": result.total_prompts,
            "completed_prompts": result.completed_prompts,
            "analysis_date": result.created_at.isoformat(),
            "analysis_duration": result.analysis_duration
        },
        "results": []
    }
    
    # 添加每個提示詞的結果
    for prompt_result in result.results_by_prompt:
        result_item = {
            "prompt": prompt_result.prompt,
            "prompt_index": prompt_result.prompt_index,
            "ai_responses": {}
        }
        
        # 添加AI回應和品牌檢測結果
        for provider, ai_response in prompt_result.ai_responses.items():
            response_data = {
                "response_text": ai_response.response_text,
                "processing_time": ai_response.processing_time,
                "error": ai_response.error,
                "brand_detections": {}
            }
            
            # 添加品牌檢測結果
            for brand, detection in ai_response.brand_detections.items():
                response_data["brand_detections"][brand] = {
                    "mentioned": detection.mentioned,
                    "reasoning": detection.reasoning
                }
            
            result_item["ai_responses"][provider] = response_data
        
        export_data["results"].append(result_item)
    
    return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)

def create_csv_export(result: SimpleAnalysisResult) -> str:
    """創建CSV格式的匯出數據"""
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 寫入標題行
    all_brands = [result.request.target_brand] + result.request.competitors
    header = ["Prompt", "AI Provider"] + all_brands + ["Response Text", "Error"]
    writer.writerow(header)
    
    # 寫入數據行
    for prompt_result in result.results_by_prompt:
        prompt = prompt_result.prompt
        
        for provider, ai_response in prompt_result.ai_responses.items():
            row = [prompt, provider]
            
            # 添加品牌檢測結果
            for brand in all_brands:
                detection = ai_response.brand_detections.get(brand)
                if detection:
                    row.append("Yes" if detection.mentioned else "No")
                else:
                    row.append("Unknown")
            
            # 添加回應文本和錯誤信息
            row.append(ai_response.response_text[:200] + "..." if len(ai_response.response_text) > 200 else ai_response.response_text)
            row.append(ai_response.error or "")
            
            writer.writerow(row)
    
    return output.getvalue()