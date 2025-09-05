#!/usr/bin/env python3
"""FireGEO Streamlit 應用啟動腳本"""

import sys
import os

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    # 導入並運行 streamlit app
    from firegeo.streamlit_app import main
    main()