"""FireGEO - AI Brand Visibility Analysis Tool - Streamlit Implementation"""

__version__ = "0.2.0"
__author__ = "FireGEO Team"
__email__ = "team@firegeo.com"

# Lazy import to avoid streamlit dependency issues during testing
def main():
    from .streamlit_app import main as streamlit_main
    return streamlit_main()

__all__ = ["main"]