from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from audit_logger import AuditLogger

# 創建認證相關的藍圖
auth_bp = Blueprint('auth', __name__)

def create_auth_decorators(user_manager):
    """創建認證裝飾器"""
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('請先登入', 'error')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function

    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('請先登入', 'error')
                return redirect(url_for('auth.login'))
            
            user = user_manager.get_user_by_id(session['user_id'])
            if not user or user.get('role') != 'admin':
                flash('需要管理員權限', 'error')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    
    return login_required, admin_required

def register_auth_routes(app, user_manager):
    """註冊認證路由"""
    
    @auth_bp.route('/login', methods=['GET', 'POST'])
    def login():
        """用戶登入"""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            if not username or not password:
                flash('請填寫用戶名和密碼', 'error')
                return render_template('login.html')
            
            user = user_manager.authenticate_user(username, password)
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                
                # 記錄登入操作
                AuditLogger.log_user_login(user['id'], user['username'])
                
                flash(f'歡迎回來，{user["username"]}！', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('用戶名或密碼錯誤', 'error')
        
        return render_template('login.html')

    @auth_bp.route('/logout')
    def logout():
        """用戶登出"""
        user_id = session.get('user_id')
        username = session.get('username', '用戶')
        
        # 記錄登出操作
        if user_id and username:
            AuditLogger.log_user_logout(user_id, username)
        
        session.clear()
        flash(f'{username} 已成功登出', 'success')
        return redirect(url_for('auth.login'))

    @auth_bp.route('/debug-login')
    def debug_login():
        """Debug 登入狀態"""
        import json
        from datetime import datetime
        
        debug_info = {
            'session': dict(session),
            'user_count': len(user_manager.load_users()),
            'admin_exists': bool(user_manager.get_user_by_username('admin')),
            'current_time': datetime.now().isoformat()
        }
        return f"<pre>{json.dumps(debug_info, indent=2, ensure_ascii=False)}</pre>"
    
    app.register_blueprint(auth_bp)