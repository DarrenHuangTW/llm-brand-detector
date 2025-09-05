"""FireGEO Models Module - Simplified"""

from .analysis import (
    SimpleAnalysisRequest,
    BrandDetectionResult,
    AIProviderResponse,
    PromptAnalysisResult,
    SimpleAnalysisResult,
    TokenUsage,
)

from .config import (
    StreamlitConfig,
    ProviderInfo,
    SUPPORTED_PROVIDERS,
    DEFAULT_PROMPTS,
)

__all__ = [
    # Analysis models
    "SimpleAnalysisRequest",
    "BrandDetectionResult",
    "AIProviderResponse", 
    "PromptAnalysisResult",
    "SimpleAnalysisResult",
    "TokenUsage",
    
    # Config models
    "StreamlitConfig",
    "ProviderInfo",
    "SUPPORTED_PROVIDERS",
    "DEFAULT_PROMPTS",
]