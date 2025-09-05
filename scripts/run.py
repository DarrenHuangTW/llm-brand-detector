#!/usr/bin/env python3
"""
FireGEO 簡單啟動腳本
"""

import sys
import os
from pathlib import Path

# 添加 src 目錄到 Python 路徑
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from firegeo.main import main
    
    if __name__ == "__main__":
        print("🔥 Starting FireGEO Monitor...")
        print("=" * 50)
        
        # 檢查環境變數文件
        env_file = project_root / ".env"
        if not env_file.exists():
            print("⚠️  Warning: .env file not found")
            print("   Please copy .env.example to .env and add your API keys")
            print("")
        
        main()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n請先執行設置腳本：")
    print("python scripts/setup.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)