# 🚀 生產環境部署指南

本文檔詳細說明如何在保護生產環境資料的前提下進行 git push 和部署。

## 🎯 核心原則

1. **資料與代碼分離** - 生產資料存放在容器外部，不會被代碼更新影響
2. **自動備份** - 每次部署前自動備份當前資料
3. **安全部署** - 使用專用腳本確保部署過程的安全性
4. **快速恢復** - 提供一鍵恢復功能，出問題時快速回滾

## 📁 資料存放架構

### 生產環境資料路徑
```
/opt/api-monitor/
├── data/                 # 資料庫和用戶資料
│   ├── api_monitor.db   # SQLite 資料庫
│   └── ...              # 其他資料檔案
├── logs/                # 應用日誌
└── uploads/             # 用戶上傳檔案
```

### 備份存放路徑
```
/var/backups/api-monitor/
├── api_monitor_backup_20250625_143022_database.db
├── api_monitor_backup_20250625_143022_data.tar.gz
├── api_monitor_backup_20250625_143022_manifest.txt
└── ...
```

## 🔄 安全部署流程

### 方案 1：使用自動化部署腳本（推薦）

```bash
# 1. 在開發機器上提交並推送代碼
git add .
git commit -m "feat: 新功能開發"
git push origin main

# 2. 在生產服務器上執行安全部署
./scripts/deploy_with_data_protection.sh

# 這個腳本會自動：
# - 備份當前資料
# - 拉取最新代碼
# - 重新部署應用
# - 驗證部署結果
```

### 方案 2：手動步驟部署

```bash
# 1. 備份當前資料
./scripts/backup_data.sh

# 2. 拉取最新代碼
git pull origin main

# 3. 重新部署（保留資料卷）
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# 4. 驗證部署
curl http://localhost:5001/health
```

## 📊 Docker Volume 資料持久化

### 開發環境（本地測試）
```yaml
# docker-compose.yml
volumes:
  - ./docker_data/data:/app/data      # 本地資料夾
  - ./docker_data/logs:/app/logs      # 本地日誌
```

### 生產環境
```yaml
# docker-compose.prod.yml
volumes:
  - /opt/api-monitor/data:/app/data   # 系統資料夾
  - /opt/api-monitor/logs:/app/logs   # 系統日誌
```

## 🔐 資料備份與恢復

### 自動備份
```bash
# 手動備份
./scripts/backup_data.sh

# 設置定時備份（可選）
# 添加到 crontab
0 2 * * * /path/to/api-monitor/scripts/backup_data.sh
```

### 恢復資料
```bash
# 查看可用備份
ls /var/backups/api-monitor/

# 恢復特定備份
./scripts/restore_data.sh api_monitor_backup_20250625_143022
```

## 🚨 緊急恢復步驟

如果部署後發現問題，按以下步驟快速恢復：

```bash
# 1. 停止當前服務
docker-compose -f docker-compose.prod.yml down

# 2. 查看最近的備份
ls -la /var/backups/api-monitor/ | grep manifest | tail -5

# 3. 恢復到最近的備份
./scripts/restore_data.sh <backup_name>

# 4. 回滾代碼到之前的版本（如需要）
git log --oneline -5
git reset --hard <previous_commit>
docker-compose -f docker-compose.prod.yml up -d --build
```

## 📋 部署檢查清單

### 部署前檢查
- [ ] 代碼已提交並推送到 GitHub
- [ ] 本地測試通過，所有功能正常
- [ ] 備份腳本可正常執行
- [ ] 生產環境資料目錄權限正確

### 部署後驗證
- [ ] 健康檢查端點正常響應
- [ ] 用戶可以正常登入
- [ ] 資料庫連接正常
- [ ] 主要功能測試通過
- [ ] 日誌無嚴重錯誤

## 🛠️ 常用管理命令

### 查看服務狀態
```bash
# 查看容器運行狀態
docker-compose -f docker-compose.prod.yml ps

# 查看應用日誌
docker-compose -f docker-compose.prod.yml logs -f api-monitor

# 查看系統資源使用
docker stats
```

### 資料庫管理
```bash
# 進入資料庫
sqlite3 /opt/api-monitor/data/api_monitor.db

# 查看資料庫大小
du -h /opt/api-monitor/data/api_monitor.db

# 備份單獨的資料庫
cp /opt/api-monitor/data/api_monitor.db /tmp/manual_backup_$(date +%Y%m%d).db
```

### 容器管理
```bash
# 進入容器檢查
docker-compose -f docker-compose.prod.yml exec api-monitor bash

# 重啟特定服務
docker-compose -f docker-compose.prod.yml restart api-monitor

# 查看容器資源使用
docker-compose -f docker-compose.prod.yml top
```

## 🔧 故障排除

### 常見問題

1. **容器無法啟動**
   ```bash
   # 檢查日誌
   docker-compose -f docker-compose.prod.yml logs api-monitor
   
   # 檢查資料目錄權限
   ls -la /opt/api-monitor/
   sudo chown -R 1000:1000 /opt/api-monitor/
   ```

2. **資料庫無法訪問**
   ```bash
   # 檢查資料庫檔案
   ls -la /opt/api-monitor/data/
   
   # 測試資料庫連接
   sqlite3 /opt/api-monitor/data/api_monitor.db ".tables"
   ```

3. **健康檢查失敗**
   ```bash
   # 手動檢查健康端點
   curl -v http://localhost:5001/health
   
   # 檢查端口占用
   netstat -tlnp | grep 5001
   ```

## 📞 支援與維護

### 監控要點
- 定期檢查備份檔案是否正常生成
- 監控磁碟使用量（資料和備份目錄）
- 觀察應用日誌中的錯誤訊息
- 定期測試恢復流程

### 維護計劃
- **日常**：檢查服務運行狀態
- **週度**：清理舊日誌和備份檔案
- **月度**：測試完整的備份恢復流程
- **季度**：檢查和更新安全設置

---

遵循此指南，你的生產環境資料將得到完善保護，即使代碼更新也不會影響用戶資料的安全性。