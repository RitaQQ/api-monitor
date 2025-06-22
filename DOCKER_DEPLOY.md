# API Monitor Docker 部署指南

本指南將幫助你使用 Docker 部署 API 監控系統到雲端服務器。

## 📋 部署前準備

### 系統要求
- Docker 20.10+
- Docker Compose 2.0+
- 至少 1GB RAM
- 至少 2GB 可用磁盤空間

### 服務器配置
```bash
# 安裝 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 啟動 Docker 服務
sudo systemctl enable docker
sudo systemctl start docker
```

## 🚀 快速部署

### 1. 克隆項目
```bash
git clone <your-repo-url>
cd api_monitor
```

### 2. 配置環境變量
```bash
# 複製環境變量模板
cp .env.example .env

# 編輯環境變量
nano .env
```

**重要**: 請務必修改以下配置：
- `SECRET_KEY`: 使用強隨機字符串
- `DEFAULT_ADMIN_PASSWORD`: 設置安全的管理員密碼
- `ALLOWED_HOSTS`: 添加你的域名

### 3. 生成安全密鑰
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
```

### 4. 啟動服務

#### 開發環境
```bash
# 僅啟動 API 服務
docker-compose up -d api-monitor

# 或啟動包含 Nginx 的完整服務
docker-compose --profile nginx up -d
```

#### 生產環境
```bash
# 創建數據目錄
sudo mkdir -p /opt/api-monitor/{data,logs}
sudo chown $USER:$USER /opt/api-monitor/{data,logs}

# 使用生產配置啟動
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 配置選項

### 環境變量配置
主要環境變量說明：

| 變量名 | 默認值 | 說明 |
|--------|--------|------|
| `SECRET_KEY` | - | Flask 安全密鑰，必須設置 |
| `DATABASE_PATH` | `/app/data/api_monitor.db` | 數據庫文件路徑 |
| `LOG_LEVEL` | `INFO` | 日誌級別 |
| `CHECK_INTERVAL` | `60` | API 檢查間隔（秒） |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | 允許的主機名 |

### Nginx 配置
如果使用 Nginx 反向代理：

1. 修改 `nginx/nginx.prod.conf` 中的域名：
```nginx
server_name your-domain.com;
```

2. 添加 SSL 證書到 `nginx/ssl/` 目錄：
```bash
mkdir -p nginx/ssl
# 複製你的證書文件
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem
```

## 📊 監控和維護

### 檢查服務狀態
```bash
# 查看服務狀態
docker-compose ps

# 查看服務日誌
docker-compose logs -f api-monitor

# 查看健康檢查
curl http://localhost:5001/health
```

### 備份數據
```bash
# 備份數據庫
docker-compose exec api-monitor cp /app/data/api_monitor.db /app/data/backup-$(date +%Y%m%d).db

# 備份到宿主機
docker cp api-monitor-app:/app/data/api_monitor.db ./backup-$(date +%Y%m%d).db
```

### 更新應用
```bash
# 拉取最新代碼
git pull

# 重新構建和部署
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🔒 安全配置

### 防火牆設置
```bash
# 僅開放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### SSL/TLS 證書
推薦使用 Let's Encrypt 免費證書：

```bash
# 安裝 Certbot
sudo apt install certbot

# 獲取證書
sudo certbot certonly --standalone -d your-domain.com

# 複製證書到 nginx 目錄
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

### 定期更新
設置定期更新和重啟：

```bash
# 添加到 crontab
0 2 * * 0 cd /path/to/api_monitor && docker-compose restart
```

## 🚨 故障排除

### 常見問題

#### 1. 權限錯誤
```bash
# 檢查數據目錄權限
ls -la data/
sudo chown -R 1000:1000 data/
```

#### 2. 端口衝突
```bash
# 檢查端口佔用
sudo netstat -tlnp | grep :5001

# 修改 docker-compose.yml 中的端口映射
ports:
  - "5002:5001"  # 改為其他端口
```

#### 3. 數據庫錯誤
```bash
# 重新初始化數據庫
docker-compose exec api-monitor python -c "
from database.db_manager import db_manager
db_manager.init_database()
"
```

#### 4. 內存不足
```bash
# 檢查系統資源
docker stats

# 清理未使用的鏡像
docker system prune -a
```

### 日誌查看
```bash
# 應用日誌
docker-compose logs -f api-monitor

# Nginx 日誌
docker-compose logs -f nginx

# 系統日誌
sudo journalctl -u docker
```

## 📈 性能優化

### 資源限制
在 `docker-compose.prod.yml` 中添加資源限制：

```yaml
api-monitor:
  deploy:
    resources:
      limits:
        memory: 512M
        cpus: "0.5"
      reservations:
        memory: 256M
        cpus: "0.25"
```

### 數據庫優化
```bash
# 數據庫真空清理（定期執行）
docker-compose exec api-monitor sqlite3 /app/data/api_monitor.db "VACUUM;"
```

## 🔄 自動部署

### GitHub Actions 示例
創建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.4
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/api-monitor
          git pull
          docker-compose -f docker-compose.prod.yml down
          docker-compose -f docker-compose.prod.yml build --no-cache
          docker-compose -f docker-compose.prod.yml up -d
```

## 📞 支援

如果遇到問題，請檢查：
1. Docker 和 Docker Compose 版本
2. 環境變量配置
3. 網絡和防火牆設置
4. 磁盤空間和內存使用情況

更多幫助請查看項目文檔或提交 Issue。