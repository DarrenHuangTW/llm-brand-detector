"""FireGEO Core Module - Simplified"""

from .simple_detector import SimpleBrandDetector
from . import ai_providers

__all__ = [
    "SimpleBrandDetector",
    "ai_providers",
]