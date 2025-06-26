#!/bin/bash

# 🔍 生產環境部署包驗證腳本
# 用途：驗證打包後的部署包完整性和功能

set -e

PACKAGE_DIR="/tmp/api-monitor-production-20250626_091136"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

if [[ ! -d "$PACKAGE_DIR" ]]; then
    echo "❌ 部署包目錄不存在: $PACKAGE_DIR"
    exit 1
fi

log "🔍 開始驗證生產環境部署包"

cd "$PACKAGE_DIR"

# 驗證必要檔案
log "📋 檢查必要檔案..."
required_files=(
    "api-monitor-production.tar.gz"
    "docker-compose.prod.yml"
    "gunicorn.conf.py"
    ".env.prod.template"
    "deploy.sh"
    "README.md"
    "PRODUCTION_DEPLOYMENT.md"
    "scripts/backup_data.sh"
    "scripts/restore_data.sh"
    "scripts/deploy_with_data_protection.sh"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        log "✅ $file"
    else
        log "❌ 缺少檔案: $file"
        exit 1
    fi
done

# 檢查檔案權限
log "🔑 檢查腳本權限..."
scripts=(
    "deploy.sh"
    "scripts/backup_data.sh"
    "scripts/restore_data.sh"
    "scripts/deploy_with_data_protection.sh"
)

for script in "${scripts[@]}"; do
    if [[ -x "$script" ]]; then
        log "✅ $script 可執行"
    else
        log "❌ $script 沒有執行權限"
        exit 1
    fi
done

# 驗證 Docker 鏡像
log "🐳 驗證 Docker 鏡像..."
if docker load < api-monitor-production.tar.gz &>/dev/null; then
    log "✅ Docker 鏡像載入成功"
    
    # 檢查鏡像資訊
    image_size=$(docker images api-monitor:production --format "table {{.Size}}" | tail -n1)
    log "📊 鏡像大小: $image_size"
    
    # 測試鏡像啟動
    log "🧪 測試鏡像啟動..."
    container_id=$(docker run -d -p 5003:5001 api-monitor:production)
    
    # 等待啟動
    sleep 15
    
    # 健康檢查
    if curl -s http://localhost:5003/health | grep -q "healthy"; then
        log "✅ 健康檢查通過"
    else
        log "❌ 健康檢查失敗"
        docker logs "$container_id"
        docker stop "$container_id" &>/dev/null || true
        exit 1
    fi
    
    # 清理測試容器
    docker stop "$container_id" &>/dev/null || true
    docker rm "$container_id" &>/dev/null || true
    
else
    log "❌ Docker 鏡像載入失敗"
    exit 1
fi

# 檢查配置檔案語法
log "⚙️ 檢查配置檔案..."

# 檢查 docker-compose 語法
if docker-compose -f docker-compose.prod.yml config &>/dev/null; then
    log "✅ docker-compose.prod.yml 語法正確"
else
    log "❌ docker-compose.prod.yml 語法錯誤"
    exit 1
fi

# 檢查 Python 語法
if python3 -m py_compile gunicorn.conf.py &>/dev/null; then
    log "✅ gunicorn.conf.py 語法正確"
else
    log "❌ gunicorn.conf.py 語法錯誤"
    exit 1
fi

# 檢查腳本語法
for script in "${scripts[@]}"; do
    if bash -n "$script" &>/dev/null; then
        log "✅ $script 語法正確"
    else
        log "❌ $script 語法錯誤"
        exit 1
    fi
done

# 計算總大小
total_size=$(du -sh . | cut -f1)
log "📦 部署包總大小: $total_size"

# 顯示檔案清單
log "📋 部署包內容清單:"
find . -type f -exec ls -lh {} \; | sort

log "🎉 部署包驗證完成！"
echo ""
echo "✅ 所有檢查項目通過"
echo "✅ Docker 鏡像可正常載入和運行"
echo "✅ 配置檔案語法正確"
echo "✅ 腳本權限設置正確"
echo ""
echo "📦 部署包已準備就緒，可以部署到生產環境！"