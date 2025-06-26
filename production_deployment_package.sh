#!/bin/bash

# 🚀 API Monitor 生產環境打包腳本
# 用途：打包生產環境 Docker 部署包，包含所有必要組件

set -e  # 遇到錯誤立即退出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_NAME="api-monitor-production-$(date +%Y%m%d_%H%M%S)"
PACKAGE_DIR="/tmp/$PACKAGE_NAME"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "🎯 開始打包 API Monitor 生產環境部署包"

# 創建打包目錄
log "創建打包目錄: $PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# 建置生產環境 Docker 鏡像
log "📦 建置生產環境 Docker 鏡像..."
cd "$SCRIPT_DIR"
docker build -f Dockerfile.prod -t api-monitor:production .

# 保存 Docker 鏡像到 tar 檔案
log "💾 保存 Docker 鏡像..."
docker save api-monitor:production | gzip > "$PACKAGE_DIR/api-monitor-production.tar.gz"

# 複製部署配置檔案
log "📋 複製部署配置檔案..."
cp docker-compose.prod.yml "$PACKAGE_DIR/"
cp gunicorn.conf.py "$PACKAGE_DIR/"
cp PRODUCTION_DEPLOYMENT.md "$PACKAGE_DIR/"

# 複製腳本檔案
log "🔧 複製管理腳本..."
mkdir -p "$PACKAGE_DIR/scripts"
cp scripts/backup_data.sh "$PACKAGE_DIR/scripts/"
cp scripts/restore_data.sh "$PACKAGE_DIR/scripts/"
cp scripts/deploy_with_data_protection.sh "$PACKAGE_DIR/scripts/"

# 創建環境變數範本
log "⚙️ 創建環境變數範本..."
cat > "$PACKAGE_DIR/.env.prod.template" << 'EOF'
# API Monitor 生產環境配置
# 複製此檔案為 .env.prod 並修改相應值

# 應用設置
SECRET_KEY=your-super-secret-key-for-production-change-this
FLASK_ENV=production
PORT=5001

# 管理員設置
ADMIN_PASSWORD=your-secure-admin-password-change-this

# 日誌級別
LOG_LEVEL=info

# 資料庫設置
DATABASE_PATH=/app/data/api_monitor.db

# 工作進程數（建議設置為 CPU 核心數 * 2 + 1）
WEB_CONCURRENCY=3
EOF

# 創建快速部署腳本
log "🚀 創建快速部署腳本..."
cat > "$PACKAGE_DIR/deploy.sh" << 'EOF'
#!/bin/bash

# API Monitor 生產環境快速部署腳本

set -e

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "🚀 開始部署 API Monitor 生產環境"

# 檢查 Docker 是否運行
if ! docker info &> /dev/null; then
    log "❌ Docker 服務未運行，請先啟動 Docker"
    exit 1
fi

# 檢查 docker-compose 是否可用
if ! command -v docker-compose &> /dev/null; then
    log "❌ docker-compose 未安裝，請先安裝"
    exit 1
fi

# 載入 Docker 鏡像
if [[ -f "api-monitor-production.tar.gz" ]]; then
    log "📥 載入 Docker 鏡像..."
    docker load < api-monitor-production.tar.gz
else
    log "❌ 找不到 Docker 鏡像檔案"
    exit 1
fi

# 檢查環境變數檔案
if [[ ! -f ".env.prod" ]]; then
    log "⚠️ 找不到 .env.prod 檔案，從範本創建..."
    cp .env.prod.template .env.prod
    log "📝 請編輯 .env.prod 檔案，設置生產環境參數"
    read -p "設置完成後按 Enter 繼續..."
fi

# 創建資料目錄
log "📁 創建資料目錄..."
sudo mkdir -p /opt/api-monitor/{data,logs,uploads,backups}
sudo chown -R 1000:1000 /opt/api-monitor/

# 停止現有服務
log "🛑 停止現有服務..."
docker-compose -f docker-compose.prod.yml down || true

# 啟動服務
log "▶️ 啟動生產環境服務..."
docker-compose -f docker-compose.prod.yml up -d

# 等待服務啟動
log "⏳ 等待服務啟動..."
sleep 15

# 健康檢查
log "🔍 檢查服務健康狀態..."
if curl -s http://localhost:5001/health | grep -q "healthy"; then
    log "✅ 部署成功！服務正常運行"
    echo ""
    echo "📋 訪問地址: http://localhost:5001"
    echo "📋 管理員帳號: admin8888"
    echo "📋 管理員密碼: 請查看 .env.prod 檔案中的 ADMIN_PASSWORD"
else
    log "❌ 服務健康檢查失敗，請檢查日誌"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

log "🎉 API Monitor 生產環境部署完成！"
EOF

chmod +x "$PACKAGE_DIR/deploy.sh"

# 設置腳本執行權限
log "🔑 設置腳本執行權限..."
chmod +x "$PACKAGE_DIR/scripts/"*.sh

# 創建 README 檔案
log "📖 創建 README 檔案..."
cat > "$PACKAGE_DIR/README.md" << 'EOF'
# API Monitor 生產環境部署包

## 🎯 包含內容

- `api-monitor-production.tar.gz` - 生產環境 Docker 鏡像
- `docker-compose.prod.yml` - 生產環境 Docker Compose 配置
- `gunicorn.conf.py` - Gunicorn WSGI 服務器配置
- `.env.prod.template` - 環境變數範本
- `deploy.sh` - 快速部署腳本
- `scripts/` - 管理腳本目錄
  - `backup_data.sh` - 資料備份腳本
  - `restore_data.sh` - 資料恢復腳本
  - `deploy_with_data_protection.sh` - 安全部署腳本
- `PRODUCTION_DEPLOYMENT.md` - 詳細部署文檔

## 🚀 快速部署

1. **準備環境變數**
   ```bash
   cp .env.prod.template .env.prod
   # 編輯 .env.prod，設置 SECRET_KEY 和 ADMIN_PASSWORD
   ```

2. **執行部署**
   ```bash
   ./deploy.sh
   ```

3. **訪問應用**
   - 地址：http://localhost:5001
   - 管理員：admin8888
   - 密碼：見 .env.prod 中的 ADMIN_PASSWORD

## 📊 資料管理

- **備份資料**: `./scripts/backup_data.sh`
- **恢復資料**: `./scripts/restore_data.sh <backup_name>`
- **安全部署**: `./scripts/deploy_with_data_protection.sh`

## 📋 系統要求

- Docker 20.10+
- Docker Compose 2.0+
- 磁碟空間：至少 2GB
- 記憶體：至少 1GB

詳細文檔請參考 `PRODUCTION_DEPLOYMENT.md`
EOF

# 創建檔案清單
log "📝 創建檔案清單..."
cd "$PACKAGE_DIR"
find . -type f -exec ls -la {} \; > file_manifest.txt

# 顯示打包結果
log "📦 打包完成！"
echo ""
echo "📋 部署包位置: $PACKAGE_DIR"
echo "📋 包含檔案:"
ls -la "$PACKAGE_DIR"
echo ""
echo "📋 部署包大小:"
du -sh "$PACKAGE_DIR"
echo ""
echo "🎯 下一步："
echo "   1. 將整個目錄複製到生產伺服器"
echo "   2. 執行 ./deploy.sh 進行部署"
echo "   3. 完整說明請參考 README.md"
EOF

chmod +x /Users/rita/api_monitor/production_deployment_package.sh