# Railway 部署指南

## 快速部署

1. **推送代碼到 GitHub**
   ```bash
   git add .
   git commit -m "Railway 部署配置"
   git push
   ```

2. **在 Railway 創建項目**
   - 前往 [Railway](https://railway.app)
   - 連接你的 GitHub 倉庫
   - 選擇自動部署

## 環境變數配置

在 Railway 項目設置中添加以下環境變數：

### 必要環境變數
```
SECRET_KEY=your-super-secret-key-for-production
FLASK_ENV=production
```

### 可選環境變數
```
DATABASE_PATH=/app/data/api_monitor.db
LOG_LEVEL=INFO
```

> **注意**: Railway 會自動設置 `PORT` 環境變數，應用會自動使用正確的端口。

## 部署檢查清單

- [x] 推送最新代碼到 GitHub
- [x] 確保 `railway.json` 配置正確
- [x] 確保 `Dockerfile` 包含數據庫初始化
- [x] 設置 Railway 環境變數
- [x] 等待部署完成
- [x] 訪問應用並測試登入

## 預設管理員帳號

```
用戶名: admin
密碼: admin123
```

## 故障排除

### 登入失敗
- 確保數據庫正確初始化
- 檢查密碼加密方式一致性
- 查看 Railway 部署日誌

### 數據庫問題
- Railway 會自動處理文件持久化
- 數據庫檔案存放在 `/app/data/api_monitor.db`
- 重新部署會重新初始化數據庫

### 端口問題
- Railway 自動分配端口
- 確保 `PORT` 環境變數設為 `5001`
- 應用監聽 `0.0.0.0:5001`

## 健康檢查

部署後訪問 `/health` 端點檢查應用狀態：
```
https://your-app.railway.app/health
```

## 日誌查看

在 Railway 控制台查看實時日誌來診斷問題。