#!/bin/bash

echo "🚀 推送 API 監控系統到 RitaQQ 的 GitHub..."
echo "目標倉庫: https://github.com/RitaQQ/api-monitor"
echo ""

# 檢查是否已設定遠端倉庫
if git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️  遠端倉庫已存在，移除現有設定..."
    git remote remove origin
fi

echo "🔗 添加遠端倉庫..."
git remote add origin "https://github.com/RitaQQ/api-monitor.git"

echo ""
echo "📤 推送所有分支到 GitHub..."

echo "推送 main 分支..."
if git push -u origin main; then
    echo "✅ main 分支推送成功"
else
    echo "❌ main 分支推送失敗"
    exit 1
fi

echo ""
echo "推送 develop 分支..."
if git push -u origin develop; then
    echo "✅ develop 分支推送成功"
else
    echo "⚠️  develop 分支推送失敗，但繼續執行..."
fi

echo ""
echo "推送 feature/enhanced-monitoring 分支..."
if git push -u origin feature/enhanced-monitoring; then
    echo "✅ feature/enhanced-monitoring 分支推送成功"
else
    echo "⚠️  feature/enhanced-monitoring 分支推送失敗，但繼續執行..."
fi

echo ""
echo "🎉 推送完成！"
echo "🌐 您的倉庫位址: https://github.com/RitaQQ/api-monitor"
echo "📖 請訪問上述網址查看您的專案"

echo ""
echo "📊 推送狀態："
git remote -v

echo ""
echo "🔧 建議的後續步驟："
echo "1. 訪問 https://github.com/RitaQQ/api-monitor"
echo "2. 編輯倉庫描述和標籤"
echo "3. 查看 README.md 檔案"
echo "4. 設定 GitHub Pages (可選)"