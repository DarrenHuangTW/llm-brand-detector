"""API金鑰驗證工具"""

import asyncio
import openai
import anthropic
import google.generativeai as genai
import httpx
from typing import Dict

async def validate_openai_key(api_key: str) -> bool:
    """驗證OpenAI API金鑰"""
    if not api_key:
        return False
    
    try:
        client = openai.AsyncOpenAI(api_key=api_key)
        # 嘗試列出模型來驗證金鑰
        await client.models.list()
        return True
    except Exception:
        return False

async def validate_anthropic_key(api_key: str) -> bool:
    """驗證Anthropic API金鑰"""
    if not api_key:
        return False
    
    try:
        client = anthropic.AsyncAnthropic(api_key=api_key)
        # 嘗試發送簡單請求來驗證
        await client.messages.create(
            model="claude-sonnet-4-0",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        return True
    except Exception:
        return False

async def validate_google_key(api_key: str) -> bool:
    """驗證Google API金鑰"""
    if not api_key:
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        # 嘗試生成內容來驗證
        response = await asyncio.get_event_loop().run_in_executor(
            None, model.generate_content, "Hi"
        )
        return bool(response.text)
    except Exception as e:
        print(f"Google validation error: {e}")
        return False

async def validate_perplexity_key(api_key: str) -> bool:
    """驗證Perplexity API金鑰"""
    if not api_key:
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        # 使用較新的模型和正確的端點
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json={
                    "model": "sonar",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5
                },
                timeout=10.0
            )
            print(f"Perplexity validation response: {response.status_code}")
            if response.status_code != 200:
                print(f"Perplexity error: {response.text}")
            return response.status_code == 200
    except Exception as e:
        print(f"Perplexity validation error: {e}")
        return False

async def validate_api_keys(
    openai_key: str = "",
    anthropic_key: str = "",
    google_key: str = "",
    perplexity_key: str = ""
) -> Dict[str, bool]:
    """並行驗證所有API金鑰"""
    
    validation_tasks = []
    
    if openai_key:
        validation_tasks.append(("OpenAI", validate_openai_key(openai_key)))
    if anthropic_key:
        validation_tasks.append(("Anthropic", validate_anthropic_key(anthropic_key)))
    if google_key:
        validation_tasks.append(("Google", validate_google_key(google_key)))
    if perplexity_key:
        validation_tasks.append(("Perplexity", validate_perplexity_key(perplexity_key)))
    
    results = {}
    
    # 執行驗證
    for provider, task in validation_tasks:
        try:
            is_valid = await asyncio.wait_for(task, timeout=10.0)
            results[provider] = is_valid
        except asyncio.TimeoutError:
            results[provider] = False
        except Exception:
            results[provider] = False
    
    return results