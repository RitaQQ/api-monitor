#!/bin/bash

# 範例推送腳本 - 請將 YOUR_USERNAME 替換為您的 GitHub 用戶名

USERNAME="YOUR_USERNAME"  # 請修改這裡

echo "🚀 推送 API 監控系統到 GitHub..."
echo "目標倉庫: https://github.com/$USERNAME/api-monitor"
echo ""

# 檢查是否已設定遠端倉庫
if git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️  遠端倉庫已存在，將使用現有設定"
else
    echo "🔗 添加遠端倉庫..."
    git remote add origin "https://github.com/$USERNAME/api-monitor.git"
fi

echo ""
echo "📤 推送所有分支到 GitHub..."

echo "推送 main 分支..."
git push -u origin main

echo "推送 develop 分支..."
git push -u origin develop

echo "推送 feature/enhanced-monitoring 分支..."
git push -u origin feature/enhanced-monitoring

echo ""
echo "✅ 推送完成！"
echo "🌐 倉庫位址: https://github.com/$USERNAME/api-monitor"

# 顯示推送後的狀態
echo ""
echo "📊 推送狀態："
git remote -v