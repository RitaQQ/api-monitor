# API 監控系統 (API Monitor)

一個功能完整的 Python Flask API 監控系統，提供即時監控、自動檢查、狀態追蹤和回應內容查看功能。

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 功能特色

### 🔍 即時監控
- 定時自動檢查 API 健康狀態（預設 60 秒間隔）
- 支援多種 HTTP 方法：GET、POST、PUT、DELETE
- 即時顯示回應時間和狀態統計

### 📊 視覺化儀表板
- 美觀的響應式網頁介面
- 即時狀態指示（正常/異常/未知）
- 自動重新整理功能

### 🔧 靈活配置
- 透過網頁介面新增/刪除 API
- 支援自訂 JSON Request Body
- 動態時間戳變數支援

### 📝 詳細記錄
- 完整的 API 回應內容查看
- 錯誤次數追蹤和通知
- 檢查歷史記錄

### 🚨 智慧通知
- 連續錯誤自動警報
- Console 和 Log 檔案記錄
- 可自訂錯誤閾值

## 📷 螢幕截圖

### 主監控頁面
- 清晰的狀態概覽
- 點擊查看 API 回應內容
- 即時統計資料

### 管理後台
- 簡易的 API 管理介面
- Request Body 編輯器
- 回應內容預覽

## 🛠 安裝與使用

### 系統需求
- Python 3.8+
- pip

### 快速開始

1. **克隆專案**
   ```bash
   git clone https://github.com/YOUR_USERNAME/api-monitor.git
   cd api-monitor
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **啟動應用程式**
   ```bash
   python app.py
   ```
   或使用啟動腳本：
   ```bash
   ./start.sh
   ```

4. **訪問網頁介面**
   - 監控儀表板: http://localhost:3000
   - 管理後台: http://localhost:3000/admin

## 📁 專案結構

```
api_monitor/
├── app.py                 # Flask 主程式
├── simple_app.py          # 簡化版主程式（無排程器）
├── api_checker.py         # API 健康檢查邏輯
├── data_manager.py        # JSON 資料管理
├── scheduler.py          # 定時檢查排程器
├── config.py             # 配置設定
├── requirements.txt      # 依賴套件清單
├── start.sh             # 啟動腳本
├── data/
│   └── apis.json        # API 資料儲存
└── templates/
    ├── index.html       # 監控儀表板頁面
    └── admin.html       # 管理後台頁面
```

## ⚙️ 配置設定

在 `config.py` 中可以調整以下設定：

```python
CHECK_INTERVAL = 60      # 檢查間隔時間（秒）
MAX_ERROR_COUNT = 3      # 觸發通知的連續錯誤次數
REQUEST_TIMEOUT = 10     # HTTP 請求超時時間
```

## 📖 使用說明

### 新增 API

1. 訪問管理後台：http://localhost:3000/admin
2. 填寫 API 資訊：
   - **名稱**: API 的顯示名稱
   - **URL**: API 端點位址
   - **HTTP 方法**: GET, POST, PUT, DELETE
   - **API 類型**: REST, GraphQL, 其他
   - **Request Body**: JSON 格式（POST/PUT 時可用）

3. 點擊「新增 API」

### 查看監控狀態

1. 訪問主頁面：http://localhost:3000
2. 查看即時統計和狀態指示
3. 點擊「📄 查看回應」查看 API 回應內容
4. 使用「🔄 立即檢查」手動觸發檢查

### 動態變數

在 Request Body 中可以使用以下動態變數：
- `{{timestamp}}`: 自動替換為當前時間戳（毫秒）

## 🔌 API 端點

系統提供以下 REST API 端點：

- `GET /` - 主監控頁面
- `GET /admin` - 管理後台
- `POST /admin/add` - 新增 API
- `POST /admin/delete/<id>` - 刪除 API
- `GET /check-now` - 立即檢查
- `GET /api/status` - 取得 JSON 格式狀態
- `GET /health` - 應用程式健康檢查

## 🎯 使用範例

### 監控 REST API
```json
{
  "name": "用戶服務 API",
  "url": "https://api.example.com/users",
  "method": "GET",
  "type": "REST"
}
```

### 監控 POST API 含 Request Body
```json
{
  "name": "搜尋 API",
  "url": "https://api.example.com/search",
  "method": "POST",
  "type": "REST",
  "request_body": {
    "query": "search term",
    "timestamp": "{{timestamp}}"
  }
}
```

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

1. Fork 這個專案
2. 建立功能分支：`git checkout -b feature/amazing-feature`
3. 提交變更：`git commit -m 'Add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 開啟 Pull Request

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

- Flask - 輕量級 Web 框架
- APScheduler - Python 任務排程
- Requests - HTTP 請求庫

---

🚀 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>