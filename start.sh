#!/bin/bash

echo "🚀 啟動 API 監控系統..."

# 檢查 Python 版本
python_version=$(python3 --version 2>/dev/null || python --version 2>/dev/null)
echo "Python 版本: $python_version"

# 設置虛擬環境
if [ ! -d "venv" ]; then
    echo "📁 建立虛擬環境..."
    python3 -m venv venv
fi

echo "🔧 啟動虛擬環境..."
source venv/bin/activate

# 安裝依賴
echo "📦 安裝依賴套件..."
pip install -r requirements.txt

# 啟動應用程式
echo "🔧 啟動 Flask 應用程式..."
echo "請訪問 http://localhost:5001 查看監控頁面"
echo "按 Ctrl+C 停止服務"
echo ""

python3 simple_app.py