# GitHub 部署指南

## 📝 專案準備完成

您的 API 監控系統已經準備好推送到 GitHub！

### 🎯 專案總覽
- **專案名稱**: api-monitor
- **描述**: Python Flask API 監控系統 - 支援即時監控、自訂 Request Body、回應內容查看
- **技術棧**: Python, Flask, APScheduler, HTML/CSS/JavaScript
- **授權**: MIT License

### 📊 專案統計
- **總檔案數**: 14 個檔案
- **程式碼行數**: 1500+ 行
- **功能模組**: 6 個 Python 模組
- **網頁模板**: 2 個響應式 HTML 模板

## 🚀 手動建立 GitHub 倉庫步驟

### 步驟 1: 在 GitHub 上建立倉庫

1. 訪問 [GitHub.com](https://github.com)
2. 點擊右上角的 "+" 按鈕
3. 選擇 "New repository"
4. 填寫倉庫資訊：
   - **Repository name**: `api-monitor`
   - **Description**: `Python Flask API 監控系統 - 支援即時監控、自訂 Request Body、回應內容查看`
   - **Visibility**: Public (或 Private，依您需求)
   - **不要勾選** "Add a README file"（我們已經有了）
   - **不要勾選** "Add .gitignore"（我們已經有了）
   - **License**: MIT License（或保持空白）

5. 點擊 "Create repository"

### 步驟 2: 推送程式碼到 GitHub

複製以下命令並在終端機中執行：

```bash
# 切換回主分支
git checkout main

# 添加遠端倉庫（請將 YOUR_USERNAME 替換為您的 GitHub 用戶名）
git remote add origin https://github.com/YOUR_USERNAME/api-monitor.git

# 推送主分支
git push -u origin main

# 推送開發分支
git push -u origin develop

# 推送功能分支
git push -u origin feature/enhanced-monitoring
```

### 步驟 3: 設定分支保護（可選）

在 GitHub 倉庫頁面：
1. 進入 Settings → Branches
2. 點擊 "Add rule"
3. 設定 `main` 分支保護規則

## 📁 當前分支結構

```
main                    # 主分支（穩定版本）
├── develop            # 開發分支
└── feature/enhanced-monitoring  # 功能分支（當前）
```

## 🔧 本地開發工作流程

```bash
# 切換到開發分支進行開發
git checkout develop

# 建立新功能分支
git checkout -b feature/new-feature

# 開發完成後合併到 develop
git checkout develop
git merge feature/new-feature

# 準備發佈時合併到 main
git checkout main
git merge develop
```

## 📋 專案檔案清單

✅ **核心程式檔案**:
- `app.py` - Flask 主程式（完整版）
- `simple_app.py` - 簡化版主程式
- `api_checker.py` - API 健康檢查邏輯
- `data_manager.py` - JSON 資料管理
- `scheduler.py` - 定時檢查排程器
- `config.py` - 配置設定

✅ **網頁模板**:
- `templates/index.html` - 監控儀表板
- `templates/admin.html` - 管理後台

✅ **配置檔案**:
- `requirements.txt` - Python 依賴清單
- `start.sh` - 啟動腳本
- `.gitignore` - Git 忽略規則
- `README.md` - 專案說明文件
- `LICENSE` - MIT 授權條款

✅ **資料檔案**:
- `data/apis.json` - API 配置和狀態資料

## 🎉 推送完成後的操作

1. **設定 GitHub Pages**（可選）:
   - 如果想要展示專案，可以啟用 GitHub Pages

2. **新增 Topics**:
   - flask
   - api-monitoring
   - python
   - web-application
   - monitoring-tool

3. **建立 Issues 和 Milestones**:
   - 可以建立 Issues 來追蹤功能需求和 Bug

4. **邀請協作者**（如需要）:
   - 在 Settings → Collaborators 中新增

## 📞 支援

如果在推送過程中遇到任何問題，請檢查：
- GitHub 用戶名和倉庫名稱是否正確
- 網路連線是否正常
- Git 認證是否設定正確

---

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>