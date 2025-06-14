#!/bin/bash

echo "🚀 啟動 API 監控系統..."

# 檢查 Python 版本
python_version=$(python3 --version 2>/dev/null || python --version 2>/dev/null)
echo "Python 版本: $python_version"

# 安裝依賴
echo "📦 安裝依賴套件..."
pip install -r requirements.txt

# 啟動應用程式
echo "🔧 啟動 Flask 應用程式..."
echo "請訪問 http://localhost:5000 查看監控頁面"
echo "按 Ctrl+C 停止服務"
echo ""

python app.py