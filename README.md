# API Monitor

一個基於 Flask 的 API 監控系統，提供實時監控、壓力測試和 Web 管理介面。

## 功能特色

- 🔍 **實時 API 監控** - 自動定期檢查 API 健康狀態
- 📊 **儀表板** - 直觀的 Web 介面顯示監控狀態
- 🔐 **用戶管理** - 支援多用戶和權限控制
- ⚡ **壓力測試** - 內建負載測試功能
- 📈 **歷史記錄** - 追蹤 API 響應時間和狀態變化
- 🎯 **靈活配置** - 支援多種 HTTP 方法和自定義參數
- 🧪 **測試案例管理** - 完整的測試專案和案例管理系統
- 📋 **審計日誌** - 完整的操作追蹤和用戶活動記錄
- 🐳 **容器化部署** - 支援 Docker 和雲端部署

## 系統要求

- Python 3.8+
- SQLite 3
- Docker (推薦部署方式)
- 支援的作業系統：Windows、macOS、Linux

## 🚀 快速開始

### 🐳 方法一：Docker 部署 (強烈推薦)

**最簡單的一鍵啟動方式：**

```bash
# 1. 克隆項目
git clone https://github.com/RitaQQ/api-monitor.git
cd api-monitor

# 2. 確保 Docker 已安裝
docker --version

# 3. 一鍵啟動 (就這麼簡單！)
docker compose up -d
```

**Docker 管理命令：**

```bash
# 查看服務狀態
docker compose ps

# 查看應用日誌
docker compose logs -f api-monitor

# 停止服務
docker compose down

# 重啟服務 (有代碼更改時)
docker compose up -d --build

# 完全清理 (包括數據)
docker compose down -v
```

**Docker 故障排除：**

```bash
# 如果遇到建置問題，清理後重試
docker system prune -f
docker compose build --no-cache
docker compose up -d
```

### 💻 方法二：本地開發環境

**macOS 用戶（推薦使用虛擬環境）：**

```bash
# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 前台運行（開發/除錯）
python simple_app.py

# 背景運行（推薦日常使用）
nohup python simple_app.py > app.log 2>&1 &

# 檢查是否運行
lsof -i :5001

# 停止背景服務
pkill -f simple_app.py
```

**Windows 用戶：**

```bash
# 創建虛擬環境
python -m venv venv
venv\Scripts\activate

# 安裝依賴並運行
pip install -r requirements.txt
python simple_app.py
```

### ☁️ 方法三：雲端部署 (Railway)

**一鍵部署到 Railway：**

1. Fork 這個項目到你的 GitHub
2. 前往 [Railway](https://railway.app) 並連接 GitHub
3. 選擇這個項目並部署
4. 設置環境變數（可選）：
   ```
   SECRET_KEY=your-super-secret-key
   PORT=5001
   ```

詳細部署指南請參考：[RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md)

## 🌐 訪問應用

啟動後訪問以下地址：

**本地訪問：**
- **主頁面**: http://localhost:5001
- **登入頁面**: http://localhost:5001/login
- **管理介面**: http://localhost:5001/admin
- **健康檢查**: http://localhost:5001/health

**區域網訪問：**
- http://[你的IP]:5001 (例如: http://192.168.1.100:5001)

## 🔑 預設帳號

```
用戶名: admin
密碼: admin123
```

> ⚠️ **安全提醒**: 生產環境請立即修改預設密碼！

## 📋 主要功能

### 🔍 API 監控
- 支援 GET、POST、PUT、DELETE 請求
- 自動檢測響應時間和狀態碼
- 可設定檢查間隔和錯誤閾值
- 動態變數支援（如 `{{timestamp}}`）

### ⚡ 壓力測試
- 並發請求測試
- 即時結果顯示
- 響應時間統計和成功率分析

### 👥 用戶管理
- 多用戶支援
- 角色權限控制 (admin/user)
- 完整的操作審計日誌

### 🧪 測試管理
- 測試案例管理 (TC格式編號)
- 測試專案組織
- CSV 匯入/匯出功能
- 產品標籤分類

### 📊 審計系統
- 完整的用戶操作記錄
- 登入/登出追蹤
- 數據變更歷史

## ⚙️ 配置說明

**主要配置文件：`config.py`**

```python
CHECK_INTERVAL = 60      # 背景檢查間隔（秒）
MAX_ERROR_COUNT = 3      # 連續錯誤閾值
REQUEST_TIMEOUT = 10     # HTTP 請求超時（秒）
```

**Docker 環境變數：**

```yaml
# docker-compose.yml 中可配置
SECRET_KEY: "your-secret-key"
PORT: 5001
FLASK_ENV: production
DATABASE_PATH: "/app/data/api_monitor.db"
```

## 🏗️ 技術架構

**核心技術棧：**
- **後端框架**: Flask 2.3.3
- **資料庫**: SQLite 3 (已從 JSON 遷移)
- **任務排程**: APScheduler 3.10.4
- **前端框架**: Bootstrap 5 + jQuery
- **容器化**: Docker + Docker Compose
- **生產部署**: Gunicorn + Gevent

**架構特色：**
- 模組化設計，易於擴展
- 完整的資料庫遷移系統
- 統一的深色主題 UI
- 響應式設計，支援行動裝置

## 📁 專案結構

```
api_monitor/
├── 📁 database/          # 資料庫管理
│   ├── db_manager.py     # SQLite 管理器
│   ├── schema.sql        # 資料庫結構
│   └── migration.py      # 資料遷移工具
├── 📁 routes/            # 路由模組
├── 📁 templates/         # Jinja2 模板
├── 📁 static/            # 靜態資源
├── 📁 data/              # 資料存儲
├── 🐳 docker-compose.yml # Docker 配置
├── 🐳 Dockerfile         # 容器建置
├── 📋 requirements.txt   # Python 依賴
└── 🚀 simple_app.py      # 主應用程式
```

## 🔧 開發指南

**本地開發設置：**

```bash
# 安裝開發依賴
pip install -r requirements.txt

# 運行測試服務器
python test_server.py

# 檢查代碼格式
# (可添加 linting 工具)
```

**Docker 開發：**

```bash
# 開發環境
docker compose up -d

# 生產環境測試
docker compose -f docker-compose.prod.yml up -d
```

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 這個項目
2. 創建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

## 📄 授權

MIT License - 詳見 [LICENSE](LICENSE) 文件

## 🆘 支援

如果遇到問題：

1. 查看 [Issues](https://github.com/RitaQQ/api-monitor/issues)
2. 查看部署指南：[RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md)
3. 查看開發文檔：[CLAUDE.md](CLAUDE.md)
4. 提交新的 Issue

---

⭐ 如果這個項目對你有幫助，請給個星星！