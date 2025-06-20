# SQLite 資料庫遷移說明

## 概述

您的 API 監控系統已成功從 JSON 檔案儲存升級為 SQLite 資料庫儲存。這次升級帶來了以下優勢：

### 🎯 主要優勢

1. **更好的資料完整性** - 外鍵約束和交易支援
2. **更高的查詢效能** - 索引和 SQL 查詢優化
3. **更強的併發支援** - 多用戶同時操作
4. **更完善的資料關聯** - 關聯式資料庫設計
5. **更大的擴展性** - 支援更複雜的查詢和統計

## 📁 資料庫結構

### 核心表格

- **users** - 用戶管理
- **apis** - API 監控配置
- **stress_test_results** - 壓力測試結果
- **product_tags** - 產品標籤
- **test_projects** - 測試專案
- **test_cases** - 測試案例
- **test_case_tags** - 測試案例與標籤關聯
- **user_stories** - 用戶故事（向後兼容）

### 資料庫檔案位置

```
data/api_monitor.db
```

## 🔄 遷移現有資料

如果您有現有的 JSON 資料需要遷移，請執行：

```bash
# 方法 1：使用遷移腳本
python migrate_to_sqlite.py

# 方法 2：手動遷移
python -c "
from database.migration import DataMigration
migration = DataMigration()
result = migration.migrate_all()
print(result)
"
```

### 遷移功能

- ✅ 自動備份原始 JSON 檔案
- ✅ 檢查並避免重複資料
- ✅ 保持資料關聯完整性
- ✅ 詳細的遷移報告

## 💻 使用方式

### 啟動應用程式

```bash
# 啟動完整版本（建議）
python simple_app.py

# 或者啟動簡化版本
python app.py
```

### 預設管理員帳號

```
用戶名: admin
密碼: admin123
```

## 🔧 開發者指南

### 資料庫管理器

```python
from database.db_manager import db_manager

# 執行查詢
results = db_manager.execute_query("SELECT * FROM users")

# 執行插入
user_id = db_manager.execute_insert("INSERT INTO users (...) VALUES (...)", params)

# 執行更新
rows_affected = db_manager.execute_update("UPDATE users SET ... WHERE ...", params)
```

### 新的管理器類別

```python
# API 管理
from data_manager import DataManager
dm = DataManager()  # 現在使用 SQLite

# 用戶管理  
from user_manager import UserManager
um = UserManager()  # 現在使用 SQLite

# 測試案例管理
from test_case_manager import TestCaseManager
tcm = TestCaseManager()  # 現在使用 SQLite
```

## 📊 資料庫維護

### 備份資料庫

```python
from database.db_manager import db_manager
db_manager.backup_database('backup/api_monitor_backup.db')
```

### 檢查資料庫狀態

```python
from database.migration import DataMigration
migration = DataMigration()
status = migration.check_migration_status()
print(status)
```

## 🔄 向後兼容性

所有現有的 API 介面保持不變：

- ✅ Web 界面完全相同
- ✅ 所有路由和功能正常
- ✅ 配置檔案格式不變
- ✅ 使用方式完全一致

## 📈 效能改善

### 查詢效能

- **索引優化** - 關鍵欄位自動建立索引
- **SQL 優化** - 使用高效的 SQL 查詢
- **關聯查詢** - 減少多次查詢

### 記憶體使用

- **按需載入** - 只載入需要的資料
- **連接池** - 重用資料庫連接
- **交易處理** - 確保資料一致性

## 🛠️ 故障排除

### 常見問題

1. **資料庫鎖定**
   ```bash
   # 檢查是否有其他程序在使用資料庫
   lsof data/api_monitor.db
   ```

2. **權限問題**
   ```bash
   # 確保 data 目錄有寫入權限
   chmod 755 data/
   chmod 644 data/api_monitor.db
   ```

3. **遷移失敗**
   ```bash
   # 檢查 JSON 檔案格式
   python -c "import json; print(json.load(open('data/apis.json')))"
   ```

### 重建資料庫

如果需要重建資料庫：

```bash
# 刪除現有資料庫
rm data/api_monitor.db

# 重新啟動應用程式會自動創建新資料庫
python simple_app.py
```

## 📝 變更日誌

### v2.0.0 - SQLite 升級

- ✅ 完全遷移到 SQLite 資料庫
- ✅ 保持所有現有功能
- ✅ 新增資料關聯和約束
- ✅ 提升查詢效能
- ✅ 支援複雜統計查詢
- ✅ 自動資料遷移工具

## 🆘 技術支援

如有問題，請檢查：

1. Python 虛擬環境是否啟動
2. 所有依賴套件是否安裝
3. data 目錄權限是否正確
4. SQLite 資料庫是否可寫入

---

**🎉 恭喜！您的 API 監控系統現在使用更強大的 SQLite 資料庫！**