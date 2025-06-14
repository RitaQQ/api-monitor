#!/bin/bash

echo "🚀 準備推送 API 監控系統到 GitHub..."
echo "請確保您已在 GitHub 上建立 'api-monitor' 倉庫"
echo ""

# 讀取 GitHub 用戶名
read -p "請輸入您的 GitHub 用戶名: " username

if [ -z "$username" ]; then
    echo "❌ 用戶名不能為空"
    exit 1
fi

echo ""
echo "📋 將執行以下操作:"
echo "1. 添加遠端倉庫: https://github.com/$username/api-monitor.git"
echo "2. 推送 main 分支"
echo "3. 推送 develop 分支"
echo "4. 推送 feature/enhanced-monitoring 分支"
echo ""

read -p "是否繼續? (y/N): " confirm

if [[ $confirm != [yY] ]]; then
    echo "❌ 操作已取消"
    exit 1
fi

echo ""
echo "🔗 添加遠端倉庫..."
git remote add origin "https://github.com/$username/api-monitor.git" 2>/dev/null || echo "遠端倉庫已存在，跳過..."

echo "📤 推送 main 分支..."
git push -u origin main

echo "📤 推送 develop 分支..."
git push -u origin develop

echo "📤 推送 feature/enhanced-monitoring 分支..."
git push -u origin feature/enhanced-monitoring

echo ""
echo "✅ 推送完成！"
echo "🌐 您的倉庫位址: https://github.com/$username/api-monitor"
echo "📖 請查看 DEPLOY.md 了解更多部署資訊"