#!/bin/bash

echo "🚀 啟動 QA Management tool..."

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

# 驗證虛擬環境是否正確啟動
echo "🔍 檢查虛擬環境狀態..."
which python3
echo "Python 路徑: $(which python3)"

# 安裝依賴
echo "📦 安裝依賴套件..."
pip install -r requirements.txt

# 檢查是否已有服務在運行
if lsof -i :5001 > /dev/null 2>&1; then
    echo "⚠️  Port 5001 已被佔用"
    echo "正在停止現有服務..."
    pkill -f simple_app.py 2>/dev/null || true
    sleep 2
fi

# 獲取本機 IP 地址
LOCAL_IP=$(ifconfig | grep "inet 192" | head -1 | awk '{print $2}' 2>/dev/null || echo "192.168.x.x")

# 啟動應用程式
echo "🔧 啟動 Flask 應用程式..."
echo "🌐 訪問地址:"
echo "   本機: http://127.0.0.1:5001"
echo "   局域網: http://$LOCAL_IP:5001"
echo ""
echo "🔧 預設管理員帳號:"
echo "   用戶名: admin"
echo "   密碼: admin123"
echo ""
echo "按 Ctrl+C 停止服務"
echo ""

# 檢查啟動模式參數
if [ "$1" = "--background" ] || [ "$1" = "-b" ]; then
    echo "🔄 在後台啟動服務..."
    nohup python3 simple_app.py > app.log 2>&1 &
    sleep 3
    if lsof -i :5001 > /dev/null 2>&1; then
        echo "✅ 服務已在後台啟動"
        echo "📋 查看日誌: tail -f app.log"
        echo "🛑 停止服務: pkill -f simple_app.py"
    else
        echo "❌ 服務啟動失敗，請檢查 app.log"
    fi
else
    echo "💡 提示: 使用 --background 或 -b 參數可在後台運行"
    echo ""
    # 前台運行
    exec python3 simple_app.py
fi