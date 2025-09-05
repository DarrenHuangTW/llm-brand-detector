"""國際化 (i18n) 支援"""

import streamlit as st

# 全局語言設定 - DEFAULT TO ENGLISH (Chinese translations preserved for future use)
CURRENT_LANGUAGE = "en"

# 多語言文本字典
TRANSLATIONS = {
    "zh-TW": {
        # 應用標題和描述
        "app_title": "🔥 FireGEO 品牌分析",
        "app_description": "**AI 驅動的多提供商品牌可見度分析平台**",
        
        # Tab 標籤
        "tab_analysis": "🎯 品牌分析",
        "tab_guide": "📚 使用指南",
        
        # 側邊欄
        "sidebar_title": "🔑 AI 提供商設定",
        "api_key": "API 金鑰",
        "model": "模型",
        "validate_apis": "🔍 驗證 API",
        "validating": "驗證 API 金鑰中...",
        "api_valid": "有效",
        "api_invalid": "無效或缺失",
        "enter_api_key": "請至少輸入一個 API 金鑰進行驗證。",
        
        # 分析設定
        "analysis_config": "📝 分析設定",
        "target_brand": "🎯 目標品牌",
        "target_brand_placeholder": "例如：OpenAI、Notion、Tesla",
        "target_brand_help": "輸入您要分析的品牌名稱",
        "competitors": "🏆 競爭對手品牌 (最多 10 個)",
        "competitors_placeholder": "每行輸入一個競爭對手：\nAnthropic\nGoogle\nMicrosoft",
        "competitors_help": "輸入競爭對手品牌，每行一個。最多 10 個競爭對手。",
        "analysis_prompts": "💬 分析提示詞 (最多 10 個)",
        "prompts_placeholder": "每行輸入一個提示詞：\n最好的 AI 公司是什麼？\n推薦頂級生產力工具\n哪個 AI 助手最受歡迎？",
        "prompts_help": "輸入分析提示詞，每行一個。最多 10 個提示詞。",
        
        # 分析按鈕和狀態
        "start_analysis": "🚀 開始分析",
        "running_analysis": "🔄 正在執行品牌分析...",
        "analysis_completed": "✅ 分析完成！",
        "analysis_failed": "❌ 分析失敗：",
        
        # 進度狀態
        "progress_initializing": "🔧 初始化 AI 提供商...",
        "progress_prompt": "📝 處理提示詞",
        "progress_calling_ai": "🤖 調用",
        "progress_calling_all": "🚀 並行調用所有提供商",
        "progress_detecting_brands": "🔍 檢測品牌提及...",
        "progress_completed_providers": "✅ 完成",
        "progress_completed_prompt": "✅ 完成提示詞",
        "progress_finalizing": "📊 整理分析結果...",
        
        # 警告訊息
        "provide_target_brand": "⚠️ 請提供目標品牌。",
        "provide_prompts": "⚠️ 請提供至少一個分析提示詞。",
        "google_api_required": "⚠️ 需要 Google API 金鑰進行品牌檢測。",
        "provide_api_key": "⚠️ 請提供至少一個 AI 提供商 API 金鑰。",
        
        # 結果顯示
        "analysis_results": "📊 分析結果",
        "configure_analysis": "🎯 在上方設定您的分析並點擊「開始分析」來開始。",
        "completed_prompts": "已完成",
        "analysis_duration": "分析時間",
        "detection_summary": "📊 品牌檢測摘要",
        "ai_responses": "🤖 AI 回應",
        "response": "回應",
        "export_options": "💾 匯出選項",
        "download_json": "📄 下載 JSON",
        "download_csv": "📊 下載 CSV",
        
        # 使用指南
        "user_guide_title": "📚 使用指南 & 技術架構",
        "how_to_use": "🚀 如何使用 FireGEO",
        "step_1": "📋 第一步：設定 API 金鑰與模型",
        "step_1_content": """1. 在左側邊欄為每個 AI 提供商輸入 API 金鑰
2. **必須提供 Google API 金鑰**（用於品牌檢測）
3. 選擇每個提供商要使用的模型
4. 點擊 \"🔍 驗證 API\" 驗證金鑰有效性""",
        "step_2": "🎯 第二步：配置分析參數",
        "step_2_content": """1. 輸入**目標品牌名稱**（如：OpenAI、Notion、Tesla）
2. 輸入**競爭對手品牌**（一行一個，最多10個）
3. 輸入**分析提示詞**（一行一個，最多10個）""",
        "step_3": "⚡ 第三步：執行分析",
        "step_3_content": """1. 點擊 \"🚀 開始分析\" 開始分析
2. 等待所有 AI 提供商回應（🚀 v2.1.0 優化：現僅需 6-8 秒！）
3. 查看品牌檢測結果、成本統計和詳細回應""",
        
        "supported_models": "🤖 支援的 AI 模型與定價",
        "result_interpretation": "📊 結果解讀",
        "result_symbols": """- **✅ 綠色勾選**：品牌被提及
- **❌ 紅色叉號**：品牌未被提及  
- **❓ 問號**：檢測失敗或無資料""",
        
        "tech_architecture": "⚙️ 技術架構與特色",
        "detection_process": "🔄 智能品牌檢測流程",
        "detection_steps": """1. **🚀 真正並行 AI 調用**: 使用 asyncio.create_task() 同時呼叫多個 AI 提供商
2. **⚡ 批量品牌檢測**: 單次 API 調用處理所有品牌（減少 75% API 調用）
3. **🔥 無速率限制**: 移除不必要的延遲，最大化響應速度
4. **🎯 智能檢測**: 使用 Gemini 2.5 Flash Lite 進行品牌識別
5. **📊 語義理解**: AI 驅動的檢測，而非簡單關鍵字匹配
6. **💰 成本追蹤**: 即時計算每次調用的 Token 用量和費用
7. **🔄 結果整合**: 統一格式展示所有分析結果""",
        
        "cost_features": "💰 成本控制特色",
        "cost_features_content": """- 即時顯示每次分析的準確成本
- 支援不同模型的成本比較
- Perplexity 搜尋費用單獨計算
- 提供經濟型、平衡型、專業型配置建議""",
        
        "info_sources": "🌐 連網搜尋 vs 內建知識",
        "auto_detection": "**自動檢測資訊來源**：",
        "source_types": """- 🌐 **即時搜尋**: Perplexity 預設使用網路搜尋
- 📚 **訓練資料**: 其他模型主要基於內建知識
- ❓ **未知來源**: 無法確定的情況""",
        
        "analysis_strategies": "🎯 分析建議策略",
        "budget_config": "**經濟型配置** (預算有限):",
        "budget_details": """- 主力：Gemini 2.5 Flash Lite
- 搜尋：Perplexity Sonar  
- 預估：每1000次分析約 $0.5-2""",
        "pro_config": "**專業型配置** (企業用戶):",
        "pro_details": """- 全模型覆蓋，最全面分析
- 預估：每1000次分析約 $10-30""",
        
        "best_practices": "💡 最佳實踐建議",
        "prompt_tips": "📝 提示詞設計技巧",
        "effective_prompts": "**有效的提示詞範例**：",
        "effective_examples": """- \"推薦最好的專案管理工具\"
- \"哪個 AI 助手最受歡迎？\"
- \"小型企業適合的客服軟體\"""",
        "avoid_prompts": "**避免的提示詞類型**：",
        "avoid_examples": """- 過於具體指向特定品牌
- 是非題（只會得到簡單回答）
- 過於抽象或模糊的問題""",
        
        "model_recommendations": "🎯 模型選擇建議",
        "daily_analysis": "**日常分析**: GPT-4o-mini + Gemini 2.5 Flash Lite",
        "important_decisions": "**重要決策**: GPT-4o + Claude Sonnet 4",
        "realtime_info": "**即時資訊**: 必須包含 Perplexity Sonar",
        "cost_control": "**成本控制**: 優先選擇 Flash Lite 和 Mini 版本",
        "best_quality": "**最佳品質**: Claude Opus 4.1 用於關鍵分析",
        
        # Model pricing details - REMOVED
        
        # 版本資訊
        "version_info": "FireGEO v2.1.0 - 高性能版",
        "ai_integration": "4 AI 提供商整合",
        "cost_tracking": "即時成本追蹤",
        "performance_boost": "80% 性能提升 (6-8秒)",
    },
    
    "en": {
        # App title and description
        "app_title": "🔥 FireGEO Brand Analysis",
        "app_description": "**AI-powered brand visibility analysis across multiple providers**",
        
        # Tab labels
        "tab_analysis": "🎯 Brand Analysis",
        "tab_guide": "📚 User Guide",
        
        # Sidebar
        "sidebar_title": "🔑 AI Provider Configuration",
        "api_key": "API Key",
        "model": "Model",
        "validate_apis": "🔍 Validate APIs",
        "validating": "Validating API keys...",
        "api_valid": "Valid",
        "api_invalid": "Invalid or missing",
        "enter_api_key": "Please enter at least one API key to validate.",
        
        # Analysis config
        "analysis_config": "📝 Analysis Configuration",
        "target_brand": "🎯 Target Brand",
        "target_brand_placeholder": "e.g., OpenAI, Notion, Tesla",
        "target_brand_help": "Enter the brand you want to analyze",
        "competitors": "🏆 Competitor Brands (max 10)",
        "competitors_placeholder": "Enter one competitor per line:\nAnthropic\nGoogle\nMicrosoft",
        "competitors_help": "Enter competitor brands, one per line. Maximum 10 competitors.",
        "analysis_prompts": "💬 Analysis Prompts (max 10)",
        "prompts_placeholder": "Enter one prompt per line:\nWhat's the best AI company?\nRecommend top productivity tools\nWhich AI assistant is most popular?",
        "prompts_help": "Enter analysis prompts, one per line. Maximum 10 prompts.",
        
        # Analysis button and status
        "start_analysis": "🚀 Start Analysis",
        "running_analysis": "🔄 Running brand analysis...",
        "analysis_completed": "✅ Analysis completed!",
        "analysis_failed": "❌ Analysis failed:",
        
        # Progress status
        "progress_initializing": "🔧 Initializing AI providers...",
        "progress_prompt": "📝 Processing prompt",
        "progress_calling_ai": "🤖 Calling",
        "progress_calling_all": "🚀 Parallel calling all providers",
        "progress_detecting_brands": "🔍 Detecting brand mentions...",
        "progress_completed_providers": "✅ Completed",
        "progress_completed_prompt": "✅ Completed prompt",
        "progress_finalizing": "📊 Finalizing analysis results...",
        
        # Warning messages
        "provide_target_brand": "⚠️ Please provide a target brand.",
        "provide_prompts": "⚠️ Please provide at least one analysis prompt.",
        "google_api_required": "⚠️ Google API key is required for brand detection.",
        "provide_api_key": "⚠️ Please provide at least one AI provider API key.",
        
        # Results display
        "analysis_results": "📊 Analysis Results",
        "configure_analysis": "🎯 Configure your analysis above and click 'Start Analysis' to begin.",
        "completed_prompts": "Completed",
        "analysis_duration": "Analysis Duration",
        "detection_summary": "📊 Brand Detection Summary",
        "ai_responses": "🤖 AI Responses",
        "response": "Response",
        "export_options": "💾 Export Options",
        "download_json": "📄 Download JSON",
        "download_csv": "📊 Download CSV",
        
        # User guide
        "user_guide_title": "📚 User Guide & Technical Architecture",
        "how_to_use": "🚀 How to Use FireGEO",
        "step_1": "📋 Step 1: Set up API Keys & Models",
        "step_1_content": """1. Enter API keys for each AI provider in the left sidebar
2. **Google API key is required** (for brand detection)
3. Select the model to use for each provider
4. Click "🔍 Validate APIs" to verify key validity""",
        "step_2": "🎯 Step 2: Configure Analysis Parameters",
        "step_2_content": """1. Enter **Target Brand Name** (e.g., OpenAI, Notion, Tesla)
2. Enter **Competitor Brands** (one per line, max 10)
3. Enter **Analysis Prompts** (one per line, max 10)""",
        "step_3": "⚡ Step 3: Execute Analysis",
        "step_3_content": """1. Click "🚀 Start Analysis" to begin
2. Wait for all AI providers to respond (🚀 v2.1.0 optimized: now just 6-8 seconds!)
3. View brand detection results, cost statistics, and detailed responses""",
        
        "supported_models": "🤖 Supported AI Models & Pricing",
        "result_interpretation": "📊 Result Interpretation",
        "result_symbols": """- **✅ Green checkmark**: Brand mentioned
- **❌ Red cross**: Brand not mentioned  
- **❓ Question mark**: Detection failed or no data""",
        
        "tech_architecture": "⚙️ Technical Architecture & Features",
        "detection_process": "🔄 Smart Brand Detection Process",
        "detection_steps": """1. **🚀 True Parallel AI Calls**: Use asyncio.create_task() to simultaneously call multiple AI providers
2. **⚡ Batch Brand Detection**: Single API call handles all brands (75% API reduction)
3. **🔥 No Rate Limiting**: Remove unnecessary delays, maximize response speed
4. **🎯 Smart Detection**: Use Gemini 2.5 Flash Lite for brand identification
5. **📊 Semantic Understanding**: AI-driven detection, not simple keyword matching
6. **💰 Cost Tracking**: Real-time calculation of Token usage and costs
7. **🔄 Result Integration**: Unified format display of all analysis results""",
        
        "cost_features": "💰 Cost Control Features",
        "cost_features_content": """- Real-time display of accurate cost per analysis
- Support for different model cost comparisons
- Perplexity search fees calculated separately
- Provides budget, balanced, and professional configuration recommendations""",
        
        "info_sources": "🌐 Online Search vs Built-in Knowledge",
        "auto_detection": "**Automatic Information Source Detection**:",
        "source_types": """- 🌐 **Real-time Search**: Perplexity uses web search by default
- 📚 **Training Data**: Other models mainly based on built-in knowledge
- ❓ **Unknown Source**: Cases where source cannot be determined""",
        
        "analysis_strategies": "🎯 Analysis Strategy Recommendations",
        "budget_config": "**Budget Configuration** (Limited budget):",
        "budget_details": """- Main: Gemini 2.5 Flash Lite
- Search: Perplexity Sonar  
- Estimate: ~$0.5-2 per 1000 analyses""",
        "pro_config": "**Professional Configuration** (Enterprise users):",
        "pro_details": """- Full model coverage, most comprehensive analysis
- Estimate: ~$10-30 per 1000 analyses""",
        
        "best_practices": "💡 Best Practice Recommendations",
        "prompt_tips": "📝 Prompt Design Tips",
        "effective_prompts": "**Effective Prompt Examples**:",
        "effective_examples": """- "Recommend the best project management tools"
- "Which AI assistant is most popular?"
- "Best customer support software for small business\"""",
        "avoid_prompts": "**Prompt Types to Avoid**:",
        "avoid_examples": """- Too specific to a particular brand
- Yes/no questions (get simple answers only)
- Too abstract or vague questions""",
        
        "model_recommendations": "🎯 Model Selection Recommendations",
        "daily_analysis": "**Daily Analysis**: GPT-4o-mini + Gemini 2.5 Flash Lite",
        "important_decisions": "**Important Decisions**: GPT-4o + Claude Sonnet 4",
        "realtime_info": "**Real-time Info**: Must include Perplexity Sonar",
        "cost_control": "**Cost Control**: Prioritize Flash Lite and Mini versions",
        "best_quality": "**Best Quality**: Claude Opus 4.1 for critical analysis",
        
        # Model pricing details - REMOVED
        
        # Version info
        "version_info": "FireGEO v2.1.0 - High Performance Edition",
        "ai_integration": "4 AI Provider Integration",
        "cost_tracking": "Real-time Cost Tracking",
        "performance_boost": "80% Performance Boost (6-8 seconds)",
    }
}

def get_text(key: str, lang: str = None) -> str:
    """獲取指定語言的文本"""
    if lang is None:
        lang = get_current_language()
    
    return TRANSLATIONS.get(lang, {}).get(key, f"[Missing: {key}]")

def set_language(lang: str):
    """設定當前語言"""
    global CURRENT_LANGUAGE
    CURRENT_LANGUAGE = lang
    if 'language' not in st.session_state:
        st.session_state['language'] = lang
    else:
        st.session_state['language'] = lang

def get_current_language() -> str:
    """獲取當前語言"""
    if 'language' in st.session_state:
        return st.session_state['language']
    return CURRENT_LANGUAGE