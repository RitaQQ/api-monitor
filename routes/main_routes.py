from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
import threading

# 創建主要功能的藍圖
main_bp = Blueprint('main', __name__)

def register_main_routes(app, data_manager, api_checker, stress_tester, user_manager, login_required):
    """註冊主要功能路由"""
    
    @main_bp.route('/')
    def index():
        """首頁 - 檢查是否已登入"""
        if 'user_id' not in session:
            # 未登入，顯示歡迎頁面
            return render_template('welcome.html')
        
        # 已登入，顯示監控頁面
        return redirect(url_for('main.dashboard'))
    
    @main_bp.route('/dashboard')
    @login_required
    def dashboard():
        """主監控頁面（需要登入）"""
        apis = data_manager.load_apis()
        
        # 計算統計資料
        stats = {
            'total': len(apis),
            'healthy': len([api for api in apis if api.get('status') == 'healthy']),
            'unhealthy': len([api for api in apis if api.get('status') == 'unhealthy']),
            'unknown': len([api for api in apis if api.get('status') == 'unknown'])
        }
        
        current_user = user_manager.get_user_by_id(session['user_id'])
        return render_template('index.html', apis=apis, stats=stats, current_user=current_user)

    @main_bp.route('/check-now')
    @login_required
    def check_now():
        """立即執行檢查"""
        return redirect(url_for('main.loading') + '?redirect=' + url_for('main.check_now_process') + '&delay=2000')

    @main_bp.route('/check-now-process')
    @login_required
    def check_now_process():
        """實際執行檢查的處理"""
        try:
            api_checker.check_all_apis()
            flash('已執行立即檢查', 'success')
        except Exception as e:
            flash(f'執行檢查時發生錯誤: {str(e)}', 'error')
            print(f"檢查錯誤詳情: {e}")
        
        return redirect(url_for('main.dashboard') + '?from_loading=true')

    @main_bp.route('/loading')
    def loading():
        """載入頁面"""
        return render_template('loading.html')

    @main_bp.route('/api/status')
    def api_status():
        """提供 JSON 格式的 API 狀態資料"""
        apis = data_manager.load_apis()
        stats = {
            'total': len(apis),
            'healthy': len([api for api in apis if api.get('status') == 'healthy']),
            'unhealthy': len([api for api in apis if api.get('status') == 'unhealthy']),
            'unknown': len([api for api in apis if api.get('status') == 'unknown'])
        }
        
        return jsonify({
            'apis': apis,
            'stats': stats
        })

    @main_bp.route('/health')
    def health_check():
        """應用程式本身的健康檢查端點"""
        return jsonify({
            'status': 'healthy',
            'message': 'API Monitor is running (simple version)'
        })

    @main_bp.route('/favicon.ico')
    def favicon():
        """Favicon 路由避免 404 錯誤"""
        return '', 204
    
    app.register_blueprint(main_bp)