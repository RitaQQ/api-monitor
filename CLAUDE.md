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
- `data/user_stories.json` - Test cases and user stories

### UI Architecture

**Template System:**
- `templates/base.html` - Unified base template with GitHub-style dark theme
- Template inheritance structure using Jinja2 `{% extends "base.html" %}`
- Responsive collapsible sidebar navigation system
- Dark theme color scheme: header `#0D1117`, content `#161B22`, text `#C9D1D9`/#8B949E`

**Key UI Features:**
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
- Admin panel for API management
- Stress testing interface with live results
- Test case management system

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
- User avatar display in collapsed mode

## Dependencies

Critical version constraints:
- `numpy<2` - Required for matplotlib compatibility
- `Flask==2.3.3` - Core framework
- `APScheduler==3.10.4` - Background task scheduling