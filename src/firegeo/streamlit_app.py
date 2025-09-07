"""LLM Brand Detector Streamlit 多語言主應用"""

import streamlit as st
import asyncio
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from firegeo.core.simple_detector import SimpleBrandDetector
from firegeo.core.ai_providers.openai_provider import OpenAIProvider
from firegeo.core.ai_providers.anthropic_provider import AnthropicProvider
from firegeo.core.ai_providers.google_provider import GoogleProvider
from firegeo.core.ai_providers.perplexity_provider import PerplexityProvider
from firegeo.models.analysis import SimpleAnalysisRequest, SimpleAnalysisResult, AIProviderResponse, PromptAnalysisResult
from firegeo.models.config import StreamlitConfig, SUPPORTED_PROVIDERS, DEFAULT_PROMPTS
from firegeo.utils.api_validation import validate_api_keys
from firegeo.utils.export import create_json_export, create_csv_export
from firegeo.localization.i18n import get_text, set_language, get_current_language

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit 頁面設定
st.set_page_config(
    page_title="LLM Brand Detector",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 語言切換組件 - COMMENTED OUT FOR ENGLISH-ONLY MODE
# def render_language_selector():
#     """渲染語言選擇器"""
#     languages = {
#         "zh-TW": "🇹🇼 繁體中文",
#         "en": "🇺🇸 English"
#     }
#     
#     current_lang = get_current_language()
#     
#     col1, col2, col3 = st.columns([1, 1, 4])
#     with col2:
#         selected_lang = st.selectbox(
#             "語言 / Language",
#             options=list(languages.keys()),
#             format_func=lambda x: languages[x],
#             index=list(languages.keys()).index(current_lang),
#             key="language_selector"
#         )
#         
#         if selected_lang != current_lang:
#             set_language(selected_lang)
#             st.rerun()

class LLMBrandDetectorApp:
    """LLM Brand Detector Streamlit應用主類"""
    
    def __init__(self):
        self.config = StreamlitConfig()
        self.init_session_state()
    
    def init_session_state(self):
        """初始化session狀態"""
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = []
        if 'current_analysis' not in st.session_state:
            st.session_state.current_analysis = None
        if 'analysis_in_progress' not in st.session_state:
            st.session_state.analysis_in_progress = False
    
    def render_api_sidebar(self) -> tuple[Dict[str, str], Dict[str, str]]:
        """渲染增強版API設定側邊欄"""
        with st.sidebar:
            st.header(get_text("sidebar_title"))
            
            api_keys = {}
            selected_models = {}
            
            for provider_key, provider_info in SUPPORTED_PROVIDERS.items():
                with st.expander(f"🤖 {provider_info.display_name}", expanded=True):
                    # API Key 輸入
                    api_keys[provider_key] = st.text_input(
                        get_text("api_key"),
                        type="password",
                        key=f"{provider_key}_api_key",
                        help=f"Enter your {provider_info.display_name} API key"
                    )
                    
                    # 模型選擇
                    if provider_info.models:
                        selected_model = st.selectbox(
                            get_text("model"),
                            provider_info.models,
                            index=provider_info.models.index(provider_info.default_model) 
                                  if provider_info.default_model in provider_info.models else 0,
                            key=f"{provider_key}_model",
                            help="Select the model to use for this provider"
                        )
                        selected_models[provider_key] = selected_model
                        
                        # 顯示模型描述
                        if hasattr(provider_info, 'model_descriptions') and provider_info.model_descriptions:
                            description = provider_info.model_descriptions.get(selected_model, "")
                            if description:
                                st.caption(f"💡 {description}")
            
            # 驗證按鈕
            if st.button(get_text("validate_apis")):
                if any(api_keys.values()):
                    with st.spinner(get_text("validating")):
                        validation_results = asyncio.run(
                            validate_api_keys(
                                openai_key=api_keys.get("openai", ""),
                                anthropic_key=api_keys.get("anthropic", ""),
                                google_key=api_keys.get("google", ""),
                                perplexity_key=api_keys.get("perplexity", "")
                            )
                        )
                        
                        for provider, is_valid in validation_results.items():
                            if is_valid:
                                st.success(f"✅ {provider}: {get_text('api_valid')}")
                            else:
                                st.error(f"❌ {provider}: {get_text('api_invalid')}")
                else:
                    st.warning(get_text("enter_api_key"))
            
            return api_keys, selected_models
    
    def render_analysis_config(self) -> SimpleAnalysisRequest:
        """渲染分析配置區域"""
        from firegeo.localization import get_text
        
        st.subheader(get_text("analysis_config"))
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            target_brand = st.text_input(
                get_text("target_brand"),
                placeholder=get_text("target_brand_placeholder"),
                help=get_text("target_brand_help")
            )
            
            competitors_text = st.text_area(
                get_text("competitors"),
                height=100,
                placeholder=get_text("competitors_placeholder"),
                help=get_text("competitors_help")
            )
        
        with col2:
            # 使用預設提示詞作為初始值
            default_prompts_text = '\n'.join(DEFAULT_PROMPTS)
            prompts_text = st.text_area(
                get_text("analysis_prompts"),
                height=150,
                value=default_prompts_text,
                placeholder=get_text("prompts_placeholder"),
                help=get_text("prompts_help")
            )
        
        # 解析輸入
        competitors = [
            line.strip() for line in competitors_text.split('\n') 
            if line.strip()
        ][:self.config.max_competitors]
        
        prompts = [
            line.strip() for line in prompts_text.split('\n') 
            if line.strip()
        ][:self.config.max_prompts]
        
        return SimpleAnalysisRequest(
            target_brand=target_brand,
            competitors=competitors,
            prompts=prompts
        )
    
    def render_analysis_button(
        self, 
        request: SimpleAnalysisRequest, 
        api_keys: Dict[str, str]
    ):
        """渲染分析按鈕和執行邏輯"""
        from firegeo.localization import get_text
        
        # 驗證輸入
        can_analyze = (
            request.target_brand and 
            request.prompts and 
            any(api_keys.values()) and
            api_keys.get("google")  # Google API是必需的（用於品牌檢測）
        )
        
        if not can_analyze:
            if not request.target_brand:
                st.warning(get_text("provide_target_brand"))
            elif not request.prompts:
                st.warning(get_text("provide_prompts"))
            elif not api_keys.get("google"):
                st.warning(get_text("google_api_required"))
            elif not any(api_keys.values()):
                st.warning(get_text("provide_api_key"))
            return
        
        if st.button(get_text("start_analysis"), type="primary", width='stretch', disabled=st.session_state.analysis_in_progress):
            # 更新請求中的API金鑰
            request.api_keys = {k: v for k, v in api_keys.items() if v}
            
            # 設置進行中狀態
            st.session_state.analysis_in_progress = True
            
            # 執行分析並顯示詳細進度
            self.run_analysis_with_progress(request)
    
    def run_analysis_with_progress(self, request: SimpleAnalysisRequest):
        """執行分析並顯示實時進度"""
        from firegeo.localization import get_text
        
        # 創建進度顯示區域
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            # 執行分析
            result = asyncio.run(self.run_analysis_with_updates(request, progress_placeholder, status_placeholder))
            
            st.session_state.current_analysis = result
            st.session_state.analysis_results.append(result)
            
            # 完成訊息
            progress_placeholder.progress(1.0, text=get_text("analysis_completed"))
            st.success(get_text("analysis_completed"))
            
        except Exception as e:
            st.error(f"{get_text('analysis_failed')} {str(e)}")
            logger.error(f"Analysis error: {e}")
        finally:
            st.session_state.analysis_in_progress = False
            st.rerun()
    
    async def run_analysis_with_updates(
        self, 
        request: SimpleAnalysisRequest,
        progress_placeholder,
        status_placeholder
    ) -> SimpleAnalysisResult:
        """執行品牌分析並實時更新進度"""
        from firegeo.localization import get_text
        
        start_time = datetime.now()
        
        result = SimpleAnalysisResult(
            request=request,
            total_prompts=len(request.prompts)
        )
        
        # 步驟 1: 初始化 AI 提供商
        total_steps = len(request.prompts) * (len([k for k in request.api_keys.values() if k]) + 1) + 2  # +2 for init and finalize
        current_step = 0
        
        progress_placeholder.progress(current_step / total_steps, text=get_text("progress_initializing"))
        status_placeholder.info(get_text("progress_initializing"))
        
        # 初始化AI提供商（包含選定的模型）
        providers = {}
        if request.api_keys.get("openai"):
            model = request.selected_models.get("openai", "gpt-4o")
            providers["OpenAI"] = OpenAIProvider(request.api_keys["openai"], model)
        if request.api_keys.get("anthropic"):
            model = request.selected_models.get("anthropic", "claude-sonnet-4-20250514")
            providers["Anthropic"] = AnthropicProvider(request.api_keys["anthropic"], model)
        if request.api_keys.get("google"):
            model = request.selected_models.get("google", "gemini-2.5-flash")
            providers["Google"] = GoogleProvider(request.api_keys["google"], model)
        if request.api_keys.get("perplexity"):
            model = request.selected_models.get("perplexity", "sonar")
            providers["Perplexity"] = PerplexityProvider(request.api_keys["perplexity"], model)
        
        if not request.api_keys.get("google"):
            raise ValueError("Google API key is required for brand detection")
        
        detector = SimpleBrandDetector(request.api_keys["google"])
        current_step += 1
        
        # 逐個處理提示詞
        for prompt_idx, prompt in enumerate(request.prompts):
            # 更新提示詞進度
            prompt_progress = f"{get_text('progress_prompt')} {prompt_idx + 1}/{len(request.prompts)}: {prompt[:50]}..."
            progress_placeholder.progress(current_step / total_steps, text=prompt_progress)
            status_placeholder.info(prompt_progress)
            
            prompt_result = PromptAnalysisResult(
                prompt=prompt,
                prompt_index=prompt_idx
            )
            
            # 並行獲取各AI提供商的回應
            parallel_progress = f"{get_text('progress_calling_all')} - Prompt {prompt_idx + 1}/{len(request.prompts)}"
            progress_placeholder.progress(current_step / total_steps, text=parallel_progress)
            status_placeholder.info(parallel_progress)
            
            # 創建並行任務
            ai_tasks = []
            for provider_name, provider in providers.items():
                task = asyncio.create_task(
                    self.process_single_provider(
                        provider_name, provider, prompt, detector, request
                    )
                )
                ai_tasks.append((provider_name, task))
            
            # 並行等待所有任務完成
            completed_providers = 0
            for provider_name, task in ai_tasks:
                try:
                    ai_response = await task
                    prompt_result.ai_responses[provider_name] = ai_response
                    completed_providers += 1
                    
                    # 更新進度
                    current_step += 1
                    parallel_progress = f"{get_text('progress_completed_providers')} {completed_providers}/{len(providers)} AI Providers - Prompt {prompt_idx + 1}/{len(request.prompts)}"
                    progress_placeholder.progress(current_step / total_steps, text=parallel_progress)
                    status_placeholder.info(parallel_progress)
                    
                except Exception as e:
                    logger.error(f"Error with {provider_name}: {e}")
                    error_response = AIProviderResponse(
                        provider=provider_name,
                        model=getattr(providers[provider_name], 'selected_model', 'unknown'),
                        prompt=prompt,
                        response_text=f"Error: {str(e)}",
                        error=str(e)
                    )
                    prompt_result.ai_responses[provider_name] = error_response
                    current_step += 1
            
            # 完成當前提示詞
            completed_progress = f"{get_text('progress_completed_prompt')} {prompt_idx + 1}/{len(request.prompts)}"
            progress_placeholder.progress(current_step / total_steps, text=completed_progress)
            status_placeholder.success(completed_progress)
            
            result.results_by_prompt.append(prompt_result)
            result.completed_prompts += 1
        
        # 最終化
        progress_placeholder.progress((total_steps - 1) / total_steps, text=get_text("progress_finalizing"))
        status_placeholder.info(get_text("progress_finalizing"))
        
        # 計算總分析時間
        end_time = datetime.now()
        result.analysis_duration = (end_time - start_time).total_seconds()
        
        return result
    
    async def process_single_provider(
        self, 
        provider_name: str, 
        provider, 
        prompt: str, 
        detector, 
        request: SimpleAnalysisRequest
    ) -> AIProviderResponse:
        """處理單個 AI 提供商的完整流程（AI 調用 + 品牌檢測）"""
        try:
            # 1. 獲取 AI 回應
            ai_response_text = await provider.get_response(prompt)
            
            # 2. 執行品牌檢測
            brand_detections = await detector.detect_multiple_brands(
                text=ai_response_text,
                target_brand=request.target_brand,
                competitors=request.competitors,
                question=prompt
            )
            
            # 3. 創建回應對象
            return AIProviderResponse(
                provider=provider_name,
                model=provider.selected_model,
                prompt=prompt,
                response_text=ai_response_text,
                brand_detections=brand_detections,
                processing_time=0.0
            )
            
        except Exception as e:
            logger.error(f"Error processing {provider_name}: {e}")
            return AIProviderResponse(
                provider=provider_name,
                model=getattr(provider, 'selected_model', 'unknown'),
                prompt=prompt,
                response_text=f"Error: {str(e)}",
                error=str(e)
            )
    
    def render_analysis_results(self):
        """渲染分析結果區域"""
        from firegeo.localization import get_text
        
        if not st.session_state.current_analysis:
            st.info(get_text("configure_analysis"))
            return
        
        result: SimpleAnalysisResult = st.session_state.current_analysis
        st.subheader(get_text("analysis_results"))
        
        # 整體進度和摘要
        progress = result.completed_prompts / max(result.total_prompts, 1)
        st.progress(progress, text=f"{get_text('completed_prompts')}: {result.completed_prompts}/{result.total_prompts} prompts")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric(get_text("target_brand"), result.request.target_brand)
        with col2:
            st.metric(get_text("competitors"), len(result.request.competitors))
        with col3:
            st.metric(get_text("analysis_duration"), f"{result.analysis_duration:.1f}s")
        
        # 逐個顯示提示詞結果
        for prompt_result in result.results_by_prompt:
            with st.expander(f"📋 Prompt {prompt_result.prompt_index + 1}: \"{prompt_result.prompt[:50]}...\"", expanded=True):
                
                # 品牌檢測摘要表格
                self.render_detection_summary_table(prompt_result, result.request)
                
                # AI回應內容
                st.subheader(get_text("ai_responses"))
                for provider, response in prompt_result.ai_responses.items():
                    with st.expander(f"▶ {provider} {get_text('response')}"):
                        if response.error:
                            st.error(f"Error: {response.error}")
                        else:
                            st.text_area(
                                f"{provider} {get_text('response')}",
                                value=response.response_text,
                                height=200,
                                disabled=True,
                                key=f"{provider}_{prompt_result.prompt_index}_response"
                            )
        
        # 匯出選項
        self.render_export_options(result)
    
    def render_detection_summary_table(self, prompt_result: PromptAnalysisResult, request: SimpleAnalysisRequest):
        """渲染品牌檢測摘要表格"""
        from firegeo.localization import get_text
        
        st.subheader(get_text("detection_summary"))
        
        # 準備表格資料
        all_brands = [request.target_brand] + request.competitors
        providers = list(prompt_result.ai_responses.keys())
        
        if not providers:
            st.warning("No brand detection results available.")
            return
        
        # 創建表格資料
        table_data = []
        for provider in providers:
            row = {"AI Provider": provider}
            ai_response = prompt_result.ai_responses.get(provider)
            
            if ai_response and ai_response.brand_detections:
                for brand in all_brands:
                    brand_result = ai_response.brand_detections.get(brand)
                    if brand_result:
                        row[brand] = "✅" if brand_result.mentioned else "❌"
                    else:
                        row[brand] = "❓"
            else:
                for brand in all_brands:
                    row[brand] = "❓"
            
            table_data.append(row)
        
        # 顯示表格
        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(df, width='stretch', hide_index=True)
        else:
            st.warning("No detection data available.")
    
    def render_export_options(self, result: SimpleAnalysisResult):
        """渲染匯出選項"""
        from firegeo.localization import get_text
        
        st.subheader(get_text("export_options"))
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # JSON匯出
            json_data = create_json_export(result)
            st.download_button(
                label=get_text("download_json"),
                data=json_data,
                file_name=f"firegeo_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # CSV匯出
            csv_data = create_csv_export(result)
            st.download_button(
                label=get_text("download_csv"), 
                data=csv_data,
                file_name=f"firegeo_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    def run(self):
        """運行主應用"""
        from firegeo.localization import get_text, get_current_language, set_language
        
        # 語言選擇器 - COMMENTED OUT FOR ENGLISH-ONLY MODE
        # with st.sidebar:
        #     st.markdown("---")
        #     current_lang = get_current_language()
        #     language_options = {"繁體中文": "zh-TW", "English": "en"}
        #     selected_language = st.selectbox(
        #         "🌐 Language / 語言",
        #         options=list(language_options.keys()),
        #         index=0 if current_lang == "zh-TW" else 1,
        #         key="language_selector"
        #     )
        #     if language_options[selected_language] != current_lang:
        #         set_language(language_options[selected_language])
        #         st.rerun()
        
        # 頁面標題
        st.title(get_text("app_title"))
        st.markdown(get_text("app_description"))
        st.markdown("---")
        
        # 建立 Tab 系統
        tab1, tab2 = st.tabs([get_text("tab_analysis"), get_text("tab_guide")])
        
        with tab1:
            # 側邊欄API設定
            api_keys, selected_models = self.render_api_sidebar()
            
            # 分析配置區域
            request = self.render_analysis_config()
            request.selected_models = selected_models  # 添加選擇的模型
            
            # 分析按鈕
            self.render_analysis_button(request, api_keys)
            
            st.markdown("---")
            
            # 結果顯示區域
            self.render_analysis_results()
        
        with tab2:
            # 使用說明頁面
            self.render_user_guide()

    def render_user_guide(self):
        """渲染使用說明頁面"""
        from firegeo.localization import get_text
        
        st.header(get_text("user_guide_title"))
        
        # 使用說明區塊
        with st.container():
            st.subheader(get_text("how_to_use"))
            
            # Step 1
            st.markdown(f"#### {get_text('step_1')}")
            st.markdown(get_text('step_1_content'))
            
            # Step 2
            st.markdown(f"#### {get_text('step_2')}")
            st.markdown(get_text('step_2_content'))
            
            # Step 3
            st.markdown(f"#### {get_text('step_3')}")
            st.markdown(get_text('step_3_content'))
        
        st.markdown("---")
        
        # 技術架構說明
        with st.container():
            st.subheader(get_text("tech_architecture"))
            
            # System overview with diagrams
            st.write(get_text('system_overview'))
            st.markdown(get_text('system_overview_content'))
            
            # Display architecture diagrams
            try:
                st.image("src/firegeo/static/architecture-diagram.png", caption="System Architecture", width="stretch")
                st.image("src/firegeo/static/workflow-diagram.png", caption="Analysis Workflow", width="stretch")
            except Exception as e:
                st.warning(f"Could not load diagrams: {str(e)}")
            
            # No additional columns needed - simplified architecture section
        
        # 最佳實踐建議
        st.markdown("---")
        with st.container():
            st.subheader(get_text("best_practices"))
            
            # Important notes first
            st.write(get_text('important_notes'))
            st.markdown(get_text('api_context'))
            
            # col1, col2 = st.columns([1, 1])
            
            # with col1:
            #     # Prompt tips
            #     st.write(get_text('prompt_tips'))
            #     st.markdown(get_text('effective_prompts'))
            #     st.markdown(get_text('effective_examples'))
            #     st.markdown(get_text('avoid_prompts'))
            #     st.markdown(get_text('avoid_examples'))
            
            # with col2:
            #     # Leave empty or minimal content as requested
            #     pass
        
        # 模型價格與選擇指南
        st.markdown("---")
        with st.container():
            st.subheader(get_text("supported_models"))
            
            # Only keep the selection guide
            st.write(get_text('selection_guide'))
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Selection factors
                st.markdown(get_text('selection_factors'))
            
            with col2:
                # Official links
                st.write(get_text('model_providers'))
                st.markdown(get_text('provider_links'))
        
        # 版本資訊
        st.markdown("---")
        with st.container():
            col1, col2 = st.columns([1, 1])
            with col1:
                st.info(f"🔥 **{get_text('version_info')}**")
            with col2:
                st.info(f"🤖 **{get_text('ai_integration')}**")
            
            # Performance boost info
            # st.success(f"⚡ **{get_text('performance_boost')}**")
            
            # Developer credit
            # st.markdown("---")
            st.success("💻 **Developed by Darren Huang with Claude Code.** Connect with me on [LinkedIn](https://www.linkedin.com/in/hunghsunhuang/)")

def main():
    """主程式入口點"""
    app = LLMBrandDetectorApp()
    app.run()

if __name__ == "__main__":
    main()