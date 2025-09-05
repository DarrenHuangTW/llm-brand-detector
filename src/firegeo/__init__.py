"""LLM Brand Detector - AI Brand Visibility Analysis Tool - Streamlit Implementation"""

__version__ = "0.2.0"
__author__ = "Darren Huang"
__email__ = "darrenhhuang@gmail.com"

# Lazy import to avoid streamlit dependency issues during testing
def main():
    from .streamlit_app import main as streamlit_main
    return streamlit_main()

__all__ = ["main"]