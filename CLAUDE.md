# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Flask-based QA Management tool that provides comprehensive quality assurance features including test case management, project tracking, user management, API monitoring, stress testing, and a web dashboard. The system supports both scheduled background monitoring and on-demand operations.

## Development Principles

### Core Development Guidelines

1. **模組化開發為主要思考邏輯**
   - 每個功能應該設計為獨立、可重用的模組
   - 遵循單一職責原則，確保每個模組只負責一個明確的功能
   - 模組間通過清晰的接口進行通信
   - 避免緊耦合，提高代碼的可維護性和可測試性

2. **完成開發後請徹底自行驗證所有功能**
   - 開發完成後必須進行全面的功能測試
   - 測試所有用戶交互路徑和邊界條件
   - 驗證錯誤處理和異常情況
   - 確保新功能不會影響現有功能
   - 在本地環境和 Docker 環境中都要測試

3. **測試資料不得打包到 Docker**
   - 任何示例資料、測試資料都不允許包含在 Docker 映像中
   - 保持生產環境的乾淨性，避免測試資料洩露
   - 初始化函數應該只創建必要的結構，不創建示例內容
   - 部署後的系統應該是空白狀態，由用戶自行添加真實資料

### Code Quality Standards

- 遵循 Python PEP 8 編碼規範
- 使用有意義的變數和函數命名
- 添加適當的註釋和文檔字串
- 實施錯誤處理和日誌記錄
- 確保代碼的安全性，防範常見攻擊

## Development Commands

### Running the Application
- `./start.sh` - **推薦方式** - 自動化啟動腳本（前台模式）
- `./start.sh --background` or `./start.sh -b` - 後台運行模式
- `python simple_app.py` - 簡化版（需先激活虛擬環境）
- `python app.py` - 完整版（包含排程器和用戶認證）

### Quick Start (推薦方式)
```bash
# 一鍵啟動（自動處理虛擬環境和依賴）
./start.sh

# 後台運行
./start.sh --background

# 查看後台日誌
tail -f app.log

# 停止服務
pkill -f simple_app.py
```

### Manual Virtual Environment Setup (如需手動設置)
```bash
# First time setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run in foreground
python simple_app.py

# Run in background
nohup python simple_app.py > app.log 2>&1 &

# Check if running
lsof -i :5001

# Stop background service
pkill -f simple_app.py
```

### Network Access
- **Local access**: http://127.0.0.1:5001
- **LAN access**: http://192.168.12.5:5001 (or your actual IP)
- Service is configured to listen on all interfaces (0.0.0.0) for LAN access
- Default admin credentials: admin8888/admin555333

### Dependencies
- `pip install -r requirements.txt` - Install Python dependencies

### Docker Deployment

**Prerequisites:**
- Install Docker Desktop for Mac: `brew install --cask docker`
- Ensure Docker Desktop is running (green status in menu bar)

**Quick Start Commands:**
```bash
# Development deployment (recommended)
docker compose up -d

# Production deployment
docker compose -f docker-compose.prod.yml up -d

# Rebuild and start (if code changes)
docker compose up -d --build

# No-cache rebuild (if having issues)
docker compose build --no-cache && docker compose up -d
```

**Management Commands:**
```bash
# Check service status
docker compose ps

# View application logs
docker compose logs -f api-monitor

# Stop all services
docker compose down

# Clean up (remove containers and networks)
docker compose down -v

# Health check
curl http://localhost:5001/health
```

**Troubleshooting:**
- If "docker: command not found": Install Docker Desktop
- If "docker daemon not running": Start Docker Desktop application
- If build fails: Try `docker system prune -f` then rebuild
- If module not found: Check `.dockerignore` file for excluded files

### Testing
- `python test_server.py` - Run test server for development

## Architecture

### Core Components

**Entry Points:**
- `app.py` - Full-featured application with user authentication, session management, and scheduled monitoring
- `simple_app.py` - Simplified version without background scheduler, suitable for development

**Data Layer:**
- `data_manager.py` - JSON file-based data persistence for APIs, handles CRUD operations
- `config.py` - Configuration management (intervals, timeouts, file paths)

**Business Logic:**
- `api_checker.py` - Core API health checking logic, supports GET/POST/PUT/DELETE methods
- `scheduler.py` - Background task scheduler using APScheduler for periodic API checks
- `stress_tester.py` - Load testing functionality for APIs
- `user_manager.py` - User authentication and role management
- `user_story_manager.py` - User story/test case management

**Data Storage:**
- `data/api_monitor.db` - SQLite database (primary data store)
- `data/apis.json` - Legacy API configurations (migrated to SQLite)
- `data/users.json` - Legacy user accounts (migrated to SQLite)
- `data/test_cases.json` - Legacy test cases (migrated to SQLite)
- `data/test_projects.json` - Legacy test project data (migrated to SQLite)
- `data/product_tags.json` - Legacy product tag definitions (migrated to SQLite)

### UI Architecture

**Template System:**
- `templates/base.html` - Unified base template with GitHub-style dark theme
- Template inheritance structure using Jinja2 `{% extends "base.html" %}`
- Responsive collapsible sidebar navigation system
- **Simplified sidebar design**: User name displayed only in logout section
- Dark theme color scheme: header `#0D1117`, content `#161B22`, text `#C9D1D9`/#8B949E`

**Key UI Features:**
- **Streamlined sidebar**: User avatar and user info section removed for cleaner design
- **User identification**: Username displayed in logout section only
- Collapsible sidebar with desktop/mobile responsive design
- State persistence using localStorage
- Bootstrap 5 + Font Awesome integration
- Unified typography and color system across all pages

### Key Features

**Authentication System:**
- Role-based access (admin/user)
- Session-based authentication with decorators (`@login_required`, `@admin_required`)

**API Monitoring:**
- Dynamic timestamp variables in request bodies (`{{timestamp}}`)
- Status tracking (healthy/unhealthy/unknown) with error count thresholds
- Response time monitoring and content inspection

**Web Interface:**
- Real-time dashboard with auto-refresh
- Admin panel for API management with collapsible sections
- Stress testing interface with live results
- **Enhanced test case management**: Full acceptance criteria display and editing
- **Simplified product tag management**: Statistics overview removed
- **Clean user management**: Avatar-free vertical layout
- Test project management with table-based views
- **Audit logging system**: Complete operation tracking for test cases and projects

**Audit and Security:**
- Comprehensive audit trail for all test case and project operations
- User authentication tracking (login/logout)
- Change history with before/after data comparison
- Admin-only access to audit logs with filtering and export capabilities
- IP address and browser tracking for security monitoring

## Configuration

Main settings in `config.py`:
- `CHECK_INTERVAL = 60` - Background check frequency (seconds)
- `MAX_ERROR_COUNT = 3` - Error threshold for notifications
- `REQUEST_TIMEOUT = 10` - HTTP request timeout

## Port Configuration

Default port is 5001 (changed from 5000 to avoid macOS ControlCenter conflicts). Port can be modified in `app.py`/`simple_app.py`.

## UI Development Notes

**Base Template System:**
All functional pages should extend `base.html` to maintain unified sidebar navigation and dark theme. Login and loading pages are exceptions as standalone pages.

**Color Scheme:**
- 主背景 (Content background): `#161B22`
- 標題列背景 (Header background): `#0D1117`
- 主文字色 (Primary text): `#C9D1D9`
- 次文字色 (Secondary text): `#8B949E`
- 邊框 (Borders): `#30363D`
- 藍色強調 (Blue accent): `#238636` - Used for hover/focus states

**Template Structure:**
```
{% extends "base.html" %}
{% block title %}Page Title{% endblock %}
{% block page_title %}Main Title{% endblock %}
{% block page_subtitle %}Subtitle{% endblock %}
{% block extra_css %}/* Page-specific CSS */{% endblock %}
{% block content %}/* Page content */{% endblock %}
{% block extra_js %}/* Page-specific JS */{% endblock %}
```

**Typography System:**
- Unified font family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
- Consistent font weights and sizes across all headings
- Font size overrides removed from individual templates to maintain consistency
- h1: 2.2em (700 weight), h2: 1.8em (600 weight), h3: 1.5em, h4: 1.3em, h5: 1.1em, h6: 1em

**Sidebar Features:**
- Collapsible with state persistence via localStorage
- Responsive design with mobile overlay
- Tooltip support for collapsed state
- Active page highlighting
- **Clean layout**: User info moved to logout section only

## Test Case Management Features

**Test Case System:**
- TC format IDs (TC00001, TC00002, etc.) for easy identification
- Table-based horizontal layout for efficient data viewing
- **Full acceptance criteria support**: Visible in table and editable in forms
- CSV import/export functionality for bulk operations (including acceptance criteria)
- Product tag integration for categorization
- **Complete form interface**: User roles and acceptance criteria fully accessible

**CSV Import/Export:**
- Template file generation with example data
- Support for batch test case creation
- Validation and error reporting
- Progress tracking during import
- All field export including timestamps and tags

**Test Project Management:**
- Table-based project overview
- Project status tracking (draft, in_progress, completed)
- Test case assignment and progress monitoring
- Statistical overview with pass/fail/blocked counts
- Responsible user assignment

**UI Improvements:**
- Collapsible sections in admin panel for cleaner interface
- **Simplified management interfaces**: Statistics overview removed from product tag management
- **Avatar-free user management**: Clean vertical layout without user avatars
- **Streamlined sidebar**: User info consolidated to logout section
- Horizontal table layouts for better information density
- Consistent dark theme across all management interfaces
- **Global user context**: Template context processor ensures consistent user access

## Dependencies

Critical version constraints:
- `numpy<2` - Required for matplotlib compatibility
- `Flask==2.3.3` - Core framework
- `APScheduler==3.10.4` - Background task scheduling
- `gunicorn==21.2.0` - Production WSGI server
- `gevent==23.7.0` - Async worker class for Gunicorn

## Recent Updates (June 22, 2025)

### Docker Deployment System
- **Complete Docker configuration**: Multi-stage production builds with security optimization
- **Docker Compose setup**: Both development and production environment configurations
- **Nginx integration**: Reverse proxy with SSL support and security headers
- **Health monitoring**: Built-in health check endpoints and container monitoring
- **Environment management**: Comprehensive `.env` configuration with security best practices
- **Production optimization**: Gunicorn WSGI server with gevent workers for high performance

### Audit Logging System  
- **Complete operation tracking**: Comprehensive audit trail for test cases and test projects
- **User activity monitoring**: Login/logout tracking with IP and browser information
- **Change history**: Before/after data comparison for all modifications
- **Admin dashboard**: Full audit log viewing with filtering, search, and CSV export
- **Security compliance**: Automatic sensitive data filtering and retention policies

### Database Migration
- **SQLite integration**: Complete migration from JSON to SQLite database
- **Schema management**: Structured database with proper indexing and constraints
- **Data integrity**: Foreign key relationships and data validation
- **Performance optimization**: Indexed queries and efficient data retrieval
- **Backup support**: Database backup and restore capabilities

### Interface Redesign
- **Restored acceptance criteria functionality**: Full display and editing in test case management
- **Simplified product tag management**: Removed statistics overview for cleaner interface
- **User management cleanup**: Removed user avatars, implemented vertical layout
- **Sidebar optimization**: User name displayed only in logout section
- **Global user context**: Added template context processor for consistent user access across all pages
- **Audit interface**: New audit logs page with advanced filtering and visualization

### Technical Improvements
- Added `@app.context_processor` in `simple_app.py` for global user access
- Updated base template to remove redundant user info sections
- Enhanced test case table to include acceptance criteria column
- Fixed user role validation in test case forms
- Implemented comprehensive audit logging throughout the application
- Added health check endpoint for Docker deployment monitoring
- Configured production-ready WSGI server with performance optimization

## Deployment Options

### Development Deployment
```bash
# Local development
python simple_app.py

# Docker development
docker-compose up -d
```

### Production Deployment
```bash
# Production with Docker
docker-compose -f docker-compose.prod.yml up -d

# Manual production setup
gunicorn --config gunicorn.conf.py simple_app:app
```

### Cloud Deployment
- **AWS/GCP/Azure**: Use Docker containers with load balancer
- **Digital Ocean**: Docker Droplet with managed database
- **Heroku**: Container deployment with add-ons
- **VPS**: Self-hosted with Docker Compose

See `DOCKER_DEPLOY.md` for detailed deployment instructions.

## Railway 部署問題調試

### 遇到的問題與解決過程

#### 問題 1: 登入失敗 (已解決)
**症狀**: 本地 Docker 可以登入，Railway 部署後無法登入，輸入正確帳密顯示密碼錯誤

**根本原因**: 密碼加密方式不一致
- 本地 Docker 建置時：`hashlib.sha256(password.encode()).hexdigest()` (無鹽值)
- 運行時驗證：`hashlib.sha256((password + salt).encode()).hexdigest()` (有鹽值)

**解決方案**: 統一密碼加密方式
```python
# database/db_manager.py:75
salt = "api_monitor_salt_2025"
password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
```

#### 問題 2: NameError 啟動錯誤 (已解決)
**症狀**: `NameError: name 'project' is not defined` 在 test_case_app.py:1146

**根本原因**: 初始化測試案例時引用未定義的 project 變數

**解決方案**: 
```python
# test_case_app.py:1146
test_project_id=None  # 改為 None，後續可分配
```

#### 問題 3: 健康檢查失敗 (已解決)
**症狀**: Railway 健康檢查連續失敗，顯示 "service unavailable"

**根本原因**: 端口配置衝突
- 應用硬編碼 port=5001
- Railway 使用動態端口通過 PORT 環境變數

**解決方案**: 動態端口配置
```python
port = int(os.environ.get('PORT', 5001))
app.run(debug=debug, host='0.0.0.0', port=port)
```

#### 問題 4: 首頁顯示異常 (已解決)
**症狀**: 訪問 Railway URL 顯示 PNG 圖示或 "Application failed to respond"

**根本原因**: 首頁路由需要登入，未登入用戶無法正常訪問

**解決方案**: 分離首頁和儀表板
```python
@main_bp.route('/')
def index():
    if 'user_id' not in session:
        return render_template('welcome.html')  # 歡迎頁面
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # 原監控邏輯
```

#### 問題 5: 502 Bad Gateway (已解決)
**症狀**: Railway 部署成功，但訪問時顯示 502 Bad Gateway

**根本原因**: 
1. Dockerfile 硬編碼端口環境變數 `PORT=5001` 
2. Docker 健康檢查使用固定端口 `localhost:5001`
3. Railway 需要使用動態端口

**解決方案**:
```dockerfile
# 移除硬編碼端口
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=simple_app.py \
    FLASK_ENV=production
    # 移除 PORT=5001

# 動態端口暴露
EXPOSE ${PORT:-5001}

# 註釋掉健康檢查
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:${PORT:-5001}/health || exit 1
```

#### 問題 6: 測試專案功能「載入專案資料失敗」(已解決)
**症狀**: 本地 Docker 正常，Railway 部署後測試專案功能無法載入，API 返回 401 錯誤

**根本原因**: 資料庫結構不一致
- 程式碼在查詢 `test_projects` 表時使用了 `start_time` 和 `end_time` 欄位
- 但 `database/schema.sql` 中的表定義缺少這些欄位
- 導致 SQL 查詢失敗，進而影響認證流程

**診斷過程**:
1. 添加詳細日誌到 `test_case_app.py`, `test_case_manager.py`, `database/db_manager.py`
2. 使用 emoji 標記和完整錯誤堆疊便於在 Railway 日誌中識別
3. 發現 SQL 查詢失敗導致整個 API 端點異常

**解決方案**:
```sql
-- 更新 database/schema.sql 添加缺失欄位
CREATE TABLE IF NOT EXISTS test_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'draft',
    responsible_user_id TEXT,
    start_time DATETIME,        -- 新增
    end_time DATETIME,          -- 新增
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (responsible_user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- 同時添加 test_results 表
CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    test_case_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'not_tested',
    notes TEXT,
    known_issues TEXT,
    blocked_reason TEXT,
    tested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES test_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
    UNIQUE(project_id, test_case_id)
);
```

**創建遷移腳本**:
```python
# database/migrate_test_projects.py
def migrate_test_projects_table():
    """遷移測試專案表，添加缺失的欄位"""
    # 檢查欄位是否已存在並添加缺失欄位
    # 確保向後兼容
```

**重要教訓**:
- Railway 每次部署都是全新環境，任何資料庫結構不一致都會暴露
- 本地 Docker 可能使用舊的資料庫檔案，掩蓋結構問題
- 必須確保 schema.sql 包含所有程式碼中使用的欄位

### 調試經驗總結

#### 🔧 調試工具和技巧

1. **詳細日誌添加**:
```python
import logging
import sys

# 配置標準輸出日誌，確保 Railway 能捕獲
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 使用 emoji 便於識別
logger.info("🚀 開始執行...")
logger.error("💥 執行失敗...")
```

2. **Railway 日誌監控**:
- 實時查看 Railway Dashboard -> Logs
- 關注應用啟動和 API 請求日誌
- 使用 emoji 快速定位關鍵信息

3. **分層調試**:
- API 層: 請求參數和響應狀態
- 業務層: 資料處理和邏輯流程  
- 資料層: SQL 查詢和錯誤詳情

#### 🚨 關鍵差異認知

**本地 vs Railway 部署環境**:

| 項目 | 本地開發 | Railway 部署 |
|------|----------|-------------|
| **狀態保持** | 持久化，增量修改 | 無狀態，每次全新 |
| **錯誤容忍** | 開發模式，寬鬆 | 生產模式，嚴格 |
| **資料庫** | 可能使用舊檔案 | 每次重新創建 |
| **環境變數** | 本地設定 | Railway 動態分配 |
| **調試方式** | 本地檔案/終端 | Railway UI 日誌 |

#### 💡 最佳實踐

1. **預防性措施**:
   - 確保 schema.sql 包含所有欄位
   - 使用遷移腳本處理結構變更
   - 在 Railway 初始化中使用非致命錯誤處理

2. **調試策略**:
   - 優先在 Railway 環境驗證問題
   - 使用詳細日誌快速定位錯誤
   - 逐個修復，避免引入新問題

3. **部署檢查清單**:
   - [ ] 資料庫 schema 完整性
   - [ ] 環境變數正確配置
   - [ ] 端口動態適配
   - [ ] 健康檢查兼容性
   - [ ] 日誌輸出完善

### 部署配置檔案

**railway.json**:
```json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "python simple_app.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**環境變數設置**:
```
SECRET_KEY=your-super-secret-key-for-production
FLASK_ENV=production
```

### 調試技巧

1. **本地與 Railway 環境差異**:
   - 本地 Docker: 持久化存儲，數據保留
   - Railway: 每次部署全新環境，無狀態

2. **錯誤隱藏原因**:
   - 條件分支可能跳過有問題的代碼
   - 環境差異暴露潛在 Bug

3. **下一步調試方向**:
   - 檢查 Railway 部署日誌
   - 測試各個模組的導入
   - 驗證數據庫初始化過程
   - 確認所有路由正確註冊