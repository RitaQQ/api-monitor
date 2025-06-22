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

### 🔄 本地 Docker 開發工作流

#### 程式碼更新方式

**方法一：重新建置並啟動 (推薦)**

```bash
# 每次程式碼修改後，重新建置映像
docker compose up -d --build

# 如果遇到快取問題，使用無快取建置
docker compose build --no-cache && docker compose up -d
```

**方法二：開發模式 Volume 掛載 (最佳開發體驗)**

創建 `docker-compose.dev.yml`：

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  api-monitor:
    build: .
    ports:
      - "5001:5001"
    volumes:
      # 將本地代碼掛載到容器內，即時同步
      - .:/app
      - /app/venv
      - /app/__pycache__
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    command: python simple_app.py
```

使用開發配置：

```bash
# 啟動開發環境
docker compose -f docker-compose.dev.yml up -d

# 修改程式碼後只需重啟 (程式碼自動同步)
docker compose -f docker-compose.dev.yml restart

# 查看即時日誌
docker compose -f docker-compose.dev.yml logs -f
```

**方法三：快速重啟**

```bash
# 如果使用 Volume 掛載，程式碼修改後重啟即可
docker compose restart api-monitor
```

#### 常用開發命令

```bash
# 開發過程中的常用操作
docker compose up -d --build      # 重新建置並啟動
docker compose logs -f api-monitor # 查看應用日誌
docker compose exec api-monitor bash # 進入容器除錯
docker compose restart api-monitor  # 重啟特定服務
docker compose down              # 停止所有服務
docker compose down -v           # 停止並清理資料

# 完全清理重來
docker system prune -f
docker compose up -d --build
```

#### 高效開發別名設置

```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
alias dcup="docker compose up -d --build"
alias dcdev="docker compose -f docker-compose.dev.yml up -d"
alias dcdown="docker compose down"
alias dclogs="docker compose logs -f"
alias dcrestart="docker compose restart"
alias dcexec="docker compose exec api-monitor bash"

# 使用別名
dcup           # 重新建置並啟動
dcdev          # 啟動開發環境
dclogs         # 查看日誌
dcrestart      # 快速重啟
```

#### 推薦的開發流程

**日常開發**：
1. 修改程式碼
2. 執行 `docker compose up -d --build`
3. 測試應用：`curl http://localhost:5001/health`
4. 查看日誌（如有問題）：`docker compose logs -f`

**高效開發**（使用 Volume 掛載）：
1. 一次性設置：`docker compose -f docker-compose.dev.yml up -d`
2. 修改程式碼（自動同步）
3. 重啟應用：`docker compose restart`
4. 即時查看日誌：`docker compose logs -f`

#### 注意事項

- **Docker 快取**：如果程式碼沒有更新，使用 `--no-cache` 強制重建
- **依賴變更**：`requirements.txt` 修改時必須重新建置
- **資料清理**：開發時可能需要 `docker compose down -v` 清理舊資料
- **效能考慮**：Volume 掛載在 Windows/Mac 上可能較慢，生產環境應使用建置映像

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

## 🐛 故障排除和調試指南

### 🔍 常見問題診斷

#### 問題 1: 測試專案功能顯示「載入專案資料失敗」

**症狀**: 本地 Docker 運行正常，但部署到 Railway 後測試專案功能無法載入

**根本原因**: 資料庫結構不一致
- 程式碼中使用了 `start_time` 和 `end_time` 欄位
- 但資料庫 schema 中 `test_projects` 表缺少這些欄位
- 導致 SQL 查詢失敗

**解決步驟**:
1. 更新資料庫 schema 添加缺失欄位
2. 創建資料庫遷移腳本
3. 在部署初始化中執行遷移

**已修復**: ✅ 已在 `database/schema.sql` 中添加缺失欄位，並創建遷移腳本

#### 問題 2: Railway 部署後 502 Bad Gateway

**症狀**: Railway 部署成功但訪問時顯示 502 錯誤

**常見原因**:
1. **端口配置衝突**: Dockerfile 硬編碼端口，但 Railway 使用動態端口
2. **健康檢查失敗**: Docker 健康檢查使用固定端口
3. **應用啟動失敗**: 初始化腳本錯誤導致應用崩潰

**解決方案**:
- 移除 Dockerfile 中的 `PORT=5001` 環境變數
- 註釋掉 Docker 健康檢查，使用 Railway 內建機制
- 程式碼中正確使用動態端口：`port = int(os.environ.get('PORT', 5001))`

#### 問題 3: 登入失敗 (本地正常，Railway 失敗)

**症狀**: 相同帳密本地可登入，Railway 部署後失敗

**根本原因**: 密碼加密方式不一致
- 建置時: `hashlib.sha256(password.encode()).hexdigest()`
- 運行時: `hashlib.sha256((password + salt).encode()).hexdigest()`

**解決方案**: 統一使用帶鹽值的加密方式

### 🔧 調試技巧和工具

#### 錯誤日誌增強

為了更好地調試 Railway 部署問題，已在關鍵位置添加詳細日誌：

```python
# 在 test_case_app.py, test_case_manager.py, database/db_manager.py 中
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 使用 emoji 標記便於識別
logger.info("🚀 開始執行...")
logger.error("💥 執行失敗...")
```

#### Railway 日誌查看

1. 進入 Railway Dashboard
2. 選擇你的應用
3. 點擊 "Logs" 標籤
4. 實時查看部署和運行日誌

#### 本地調試命令

```bash
# 檢查資料庫結構
sqlite3 data/api_monitor.db ".schema test_projects"

# 查看錯誤日誌
tail -f app.log

# 檢查端口占用
lsof -i :5001

# 測試健康檢查
curl http://localhost:5001/health
```

### 🏗️ 本地 vs 遠端部署關鍵差異

#### 環境差異對比

| 項目 | 本地開發 | Docker 本地 | Railway 部署 |
|------|----------|-------------|--------------|
| **環境狀態** | 持久化 | 容器隔離 | 無狀態，每次全新 |
| **資料庫** | 增量更新 | 容器內持久 | 每次重新創建 |
| **端口配置** | 固定 5001 | 固定 5001 | 動態分配 |
| **錯誤容忍** | 開發模式高 | 中等 | 生產模式嚴格 |
| **日誌查看** | 本地檔案 | docker logs | Railway UI |
| **環境變數** | .env 或系統 | docker-compose | Railway 設定 |

#### 關鍵注意事項

**🔥 Railway 部署特殊性**:
1. **無狀態環境**: 每次部署都是全新環境，不保留任何狀態
2. **動態端口**: 必須使用 `PORT` 環境變數，不能硬編碼
3. **資料庫重建**: 每次都會重新執行 schema.sql，必須確保結構完整
4. **嚴格模式**: 任何 SQL 錯誤都會導致應用無法啟動

**💡 最佳實踐**:
- 使用遷移腳本確保資料庫向後兼容
- 添加詳細日誌以便快速定位問題
- 在 Railway 初始化中使用非致命錯誤處理
- 測試時優先使用 Railway 部署環境驗證

**🚨 常見陷阱**:
- 本地 Docker 可能使用舊的資料庫檔案，掩蓋結構問題
- 條件分支可能在本地跳過有問題的代碼路徑
- 環境變數差異導致不同的執行路徑

#### 調試建議流程

1. **本地驗證**: 先確保本地環境完全正常
2. **Docker 測試**: 使用 `docker compose build --no-cache` 清理測試
3. **Railway 部署**: 推送並查看 Railway 日誌
4. **錯誤定位**: 使用詳細日誌快速找到問題點
5. **逐步修復**: 每次只修復一個問題，避免引入新問題

---

⭐ 如果這個項目對你有幫助，請給個星星！