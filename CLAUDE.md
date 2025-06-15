# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Flask-based API monitoring system that provides real-time API health checking, user management, stress testing, and a web dashboard. The system supports both scheduled background monitoring and on-demand API checks.

## Development Commands

### Running the Application
- `python app.py` - Run full application with scheduler and user authentication
- `python simple_app.py` - Run simplified version without scheduler
- `./start.sh` - Automated startup script with dependency installation

### Virtual Environment Setup (Required for macOS)
```bash
# First time setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python simple_app.py

# Subsequent runs
source venv/bin/activate
python simple_app.py
```

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

## Configuration

Main settings in `config.py`:
- `CHECK_INTERVAL = 60` - Background check frequency (seconds)
- `MAX_ERROR_COUNT = 3` - Error threshold for notifications
- `REQUEST_TIMEOUT = 10` - HTTP request timeout

## Port Configuration

Default port is 5000, but can be overridden via environment or code modification in app.py/simple_app.py.