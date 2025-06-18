# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Flask-based API monitoring system that provides real-time API health checking, user management, stress testing, and a web dashboard. The system supports both scheduled background monitoring and on-demand API checks.

## Development Commands

### Running the Application
- `python app.py` - Run full application with scheduler and user authentication
- `python simple_app.py` - Run simplified version without scheduler
- `./start.sh` - Automated startup script (foreground mode)
- `./start.sh --background` or `./start.sh -b` - Start in background mode

### Virtual Environment Setup (Required for macOS)
```bash
# First time setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run in foreground (for development/debugging)
source venv/bin/activate
python simple_app.py

# Run in background (recommended for normal use)
source venv/bin/activate
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
- Default admin credentials: admin/admin123

### Dependencies
- `pip install -r requirements.txt` - Install Python dependencies

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
- `data/apis.json` - API configurations and status data
- `data/users.json` - User accounts and authentication data
- `data/test_cases.json` - Test cases data with TC format IDs
- `data/test_projects.json` - Test project management data
- `data/product_tags.json` - Product tag definitions

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

## Recent Updates (June 18, 2025)

### Interface Redesign
- **Restored acceptance criteria functionality**: Full display and editing in test case management
- **Simplified product tag management**: Removed statistics overview for cleaner interface
- **User management cleanup**: Removed user avatars, implemented vertical layout
- **Sidebar optimization**: User name displayed only in logout section
- **Global user context**: Added template context processor for consistent user access across all pages

### Technical Improvements
- Added `@app.context_processor` in `simple_app.py` for global user access
- Updated base template to remove redundant user info sections
- Enhanced test case table to include acceptance criteria column
- Fixed user role validation in test case forms