#!/usr/bin/env python3
"""
FireGEO Python 項目設置腳本
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List


def run_command(cmd: List[str], description: str) -> bool:
    """執行命令並返回結果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} 完成")
        if result.stdout and result.stdout.strip():
            print(f"   輸出: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失敗: {e}")
        if e.stderr:
            print(f"   錯誤: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} 失敗: 命令未找到")
        return False


def check_python_version():
    """檢查 Python 版本"""
    print("🐍 檢查 Python 版本...")
    version = sys.version_info
    if version < (3, 11):
        print(f"❌ 需要 Python 3.11 或更高版本，當前版本: {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python 版本檢查通過: {version.major}.{version.minor}.{version.micro}")


def check_uv_installation():
    """檢查並安裝 uv"""
    print("📦 檢查 uv 安裝狀態...")
    try:
        result = subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ uv 已安裝")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv 未安裝，正在安裝...")
        try:
            # 嘗試使用 pip 安裝 uv
            subprocess.run([sys.executable, "-m", "pip", "install", "uv"], check=True)
            print("✅ uv 安裝完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ uv 安裝失敗，請手動安裝：")
            print("   pip install uv")
            return False


def create_env_file():
    """創建環境變數文件"""
    print("⚙️ 創建環境變數文件...")
    
    env_example = Path(".env.example")
    env_local = Path(".env")
    
    if env_example.exists() and not env_local.exists():
        import shutil
        shutil.copy(env_example, env_local)
        print("✅ .env 文件創建完成（從 .env.example 複製）")
        print("⚠️ 請編輯 .env 文件，添加您的 API Keys")
    elif env_local.exists():
        print("✅ .env 文件已存在")
    else:
        print("⚠️ 未找到 .env.example，請手動創建 .env 文件")


def install_dependencies():
    """安裝項目依賴"""
    print("📥 安裝項目依賴...")
    
    # 檢查 pyproject.toml 是否存在
    if not Path("pyproject.toml").exists():
        print("❌ 未找到 pyproject.toml 文件")
        return False
    
    # 嘗試使用 uv 同步依賴
    if run_command(["uv", "sync", "--dev"], "同步依賴包"):
        return True
    
    # 如果 uv 失敗，嘗試使用 pip
    print("🔄 uv 同步失敗，嘗試使用 pip 安裝...")
    return run_command([
        sys.executable, "-m", "pip", "install", 
        "gradio", "openai", "anthropic", "google-genai", 
        "httpx", "pydantic", "pydantic-settings", "python-dotenv",
        "pandas", "plotly", "aiofiles", "loguru"
    ], "使用 pip 安裝核心依賴")


def setup_data_directory():
    """設置數據目錄"""
    print("💾 設置數據目錄...")
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # 創建空的分析文件
    analyses_file = data_dir / "brand-analyses.json"
    if not analyses_file.exists():
        analyses_file.write_text("[]", encoding='utf-8')
        print("✅ 創建空的分析數據文件")
    
    print("✅ 數據目錄設置完成")


def main():
    """主設置流程"""
    print("🔥 FireGEO Python 項目設置")
    print("=" * 50)
    
    # 檢查系統要求
    check_python_version()
    
    if not check_uv_installation():
        print("⚠️ uv 安裝失敗，將使用 pip 作為備選方案")
    
    # 設置項目
    create_env_file()
    
    if not install_dependencies():
        print("❌ 設置失敗：無法安裝依賴")
        print("請手動安裝以下套件：")
        print("pip install gradio openai anthropic google-genai httpx pydantic pydantic-settings python-dotenv pandas plotly aiofiles loguru")
        sys.exit(1)
    
    setup_data_directory()
    
    print("\n🎉 設置完成！")
    print("\n下一步：")
    print("1. 編輯 .env 文件，添加您的 API Keys")
    print("2. 運行應用：")
    print("   - 如果有 uv: uv run python -m src.firegeo.main")
    print("   - 或者直接: python -m src.firegeo.main")
    print("   - 或者: python scripts/run.py")


if __name__ == "__main__":
    main()