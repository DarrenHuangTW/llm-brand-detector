#!/usr/bin/env python3
"""簡單的 LLM Brand Detector Streamlit 啟動腳本"""

import os
import sys
import subprocess

# 添加 src 目錄到 Python 路徑
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 設置環境變數
os.environ['PYTHONPATH'] = src_path + os.pathsep + os.environ.get('PYTHONPATH', '')

# 運行 streamlit
if __name__ == "__main__":
    streamlit_file = os.path.join(src_path, 'firegeo', 'streamlit_app.py')
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', streamlit_file])