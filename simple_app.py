from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from data_manager import DataManager
from api_checker import APIChecker
from stress_tester import StressTester
from user_manager import UserManager
from user_story_manager import UserStoryManager
from test_case_app import create_test_case_routes, init_test_case_data
from config import Config
import os
import threading
import json
from datetime import datetime
from functools import wraps

app = Flask(__name__)
config = Config()
app.config.from_object(config)

# 初始化組件
data_manager = DataManager(config.DATA_FILE)
api_checker = APIChecker(data_manager)
stress_tester = StressTester(data_manager)
user_manager = UserManager()
user_story_manager = UserStoryManager()

# 初始化測試案例管理
test_case_manager = init_test_case_data()
create_test_case_routes(app, test_case_manager)

# 認證裝飾器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('請先登入', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('請先登入', 'error')
            return redirect(url_for('login'))
        
        user = user_manager.get_user_by_id(session['user_id'])
        if not user or user.get('role') != 'admin':
            flash('需要管理員權限', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# 認證路由
@app.route('/login', methods=['GET', 'POST'])
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
            flash(f'歡迎回來，{user["username"]}！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用戶名或密碼錯誤', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """用戶登出"""
    username = session.get('username', '用戶')
    session.clear()
    flash(f'{username} 已成功登出', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """主監控頁面"""
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

@app.route('/admin')
@admin_required
def admin():
    """管理後台頁面"""
    apis = data_manager.load_apis()
    return render_template('admin.html', apis=apis)

@app.route('/admin/add', methods=['POST'])
@admin_required
def add_api():
    """新增 API"""
    name = request.form.get('name', '').strip()
    url = request.form.get('url', '').strip()
    api_type = request.form.get('type', 'REST').strip()
    method = request.form.get('method', 'GET').strip()
    request_body = request.form.get('request_body', '').strip()
    
    # 取得壓力測試參數
    concurrent_requests = int(request.form.get('concurrent_requests', 1))
    duration_seconds = int(request.form.get('duration_seconds', 10))
    interval_seconds = float(request.form.get('interval_seconds', 1.0))
    
    if not name or not url:
        flash('請填寫完整的 API 名稱和 URL', 'error')
        return redirect(url_for('admin'))
    
    # 檢查 URL 是否已存在
    existing_apis = data_manager.load_apis()
    if any(api.get('url') == url for api in existing_apis):
        flash('這個 URL 已經存在於監控清單中', 'error')
        return redirect(url_for('admin'))
    
    # 驗證 request body 格式（如果有填寫）
    if request_body and method in ['POST', 'PUT', 'PATCH']:
        try:
            import json as json_module
            json_module.loads(request_body)  # 驗證是否為有效的 JSON
        except json_module.JSONDecodeError:
            flash('Request Body 必須是有效的 JSON 格式', 'error')
            return redirect(url_for('admin'))
    
    # 驗證壓力測試參數
    if not (1 <= concurrent_requests <= 100):
        flash('併發請求數必須在 1-100 之間', 'error')
        return redirect(url_for('admin'))
    
    if not (5 <= duration_seconds <= 300):
        flash('持續時間必須在 5-300 秒之間', 'error')
        return redirect(url_for('admin'))
    
    if not (0.1 <= interval_seconds <= 10):
        flash('請求間隔必須在 0.1-10 秒之間', 'error')
        return redirect(url_for('admin'))
    
    try:
        new_api = data_manager.add_api(
            name, url, api_type, method, 
            request_body if request_body else None,
            concurrent_requests, duration_seconds, interval_seconds
        )
        flash(f'成功新增 API: {name} ({method}) - 壓力測試配置已設定', 'success')
        
        # 立即檢查新增的 API
        try:
            api_checker.check_all_apis()
        except Exception as check_error:
            print(f"檢查 API 時發生錯誤: {check_error}")
        
    except Exception as e:
        flash(f'新增 API 時發生錯誤: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/delete/<api_id>', methods=['POST'])
@admin_required
def delete_api(api_id):
    """刪除 API"""
    try:
        if data_manager.delete_api(api_id):
            flash('API 已成功刪除', 'success')
        else:
            flash('找不到要刪除的 API', 'error')
    except Exception as e:
        flash(f'刪除 API 時發生錯誤: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/edit/<api_id>')
@admin_required
def edit_api(api_id):
    """編輯 API 頁面"""
    api = data_manager.get_api_by_id(api_id)
    if not api:
        flash('找不到指定的 API', 'error')
        return redirect(url_for('admin'))
    return render_template('edit_api.html', api=api)

@app.route('/admin/edit/<api_id>', methods=['POST'])
@admin_required
def update_api(api_id):
    """更新 API"""
    name = request.form.get('name', '').strip()
    url = request.form.get('url', '').strip()
    api_type = request.form.get('type', 'REST').strip()
    method = request.form.get('method', 'GET').strip()
    request_body = request.form.get('request_body', '').strip()
    
    # 取得壓力測試參數
    concurrent_requests = int(request.form.get('concurrent_requests', 1))
    duration_seconds = int(request.form.get('duration_seconds', 10))
    interval_seconds = float(request.form.get('interval_seconds', 1.0))
    
    if not name or not url:
        flash('請填寫完整的 API 名稱和 URL', 'error')
        return redirect(url_for('edit_api', api_id=api_id))
    
    # 檢查 URL 是否與其他 API 重複（排除當前 API）
    existing_apis = data_manager.load_apis()
    for api in existing_apis:
        if api.get('id') != api_id and api.get('url') == url:
            flash('這個 URL 已經存在於其他 API 中', 'error')
            return redirect(url_for('edit_api', api_id=api_id))
    
    # 驗證 request body 格式（如果有填寫）
    if request_body and method in ['POST', 'PUT', 'PATCH']:
        try:
            import json as json_module
            json_module.loads(request_body)  # 驗證是否為有效的 JSON
        except json_module.JSONDecodeError:
            flash('Request Body 必須是有效的 JSON 格式', 'error')
            return redirect(url_for('edit_api', api_id=api_id))
    
    # 驗證壓力測試參數
    if not (1 <= concurrent_requests <= 100):
        flash('併發請求數必須在 1-100 之間', 'error')
        return redirect(url_for('edit_api', api_id=api_id))
    
    if not (5 <= duration_seconds <= 300):
        flash('持續時間必須在 5-300 秒之間', 'error')
        return redirect(url_for('edit_api', api_id=api_id))
    
    if not (0.1 <= interval_seconds <= 10):
        flash('請求間隔必須在 0.1-10 秒之間', 'error')
        return redirect(url_for('edit_api', api_id=api_id))
    
    try:
        success = data_manager.update_api(
            api_id, name, url, api_type, method, 
            request_body if request_body else None,
            concurrent_requests, duration_seconds, interval_seconds
        )
        
        if success:
            flash(f'成功更新 API: {name} ({method})', 'success')
            
            # 立即檢查更新後的 API
            try:
                api_checker.check_all_apis()
            except Exception as check_error:
                print(f"檢查 API 時發生錯誤: {check_error}")
            
            return redirect(url_for('admin'))
        else:
            flash('找不到要更新的 API', 'error')
            return redirect(url_for('edit_api', api_id=api_id))
        
    except Exception as e:
        flash(f'更新 API 時發生錯誤: {str(e)}', 'error')
        return redirect(url_for('edit_api', api_id=api_id))

@app.route('/check-now')
@login_required
def check_now():
    """立即執行檢查"""
    # 先顯示loading頁面，然後重定向到結果頁面
    return redirect(url_for('loading') + '?redirect=' + url_for('check_now_process') + '&delay=2000')

@app.route('/check-now-process')
@login_required
def check_now_process():
    """實際執行檢查的處理"""
    try:
        api_checker.check_all_apis()
        flash('已執行立即檢查', 'success')
    except Exception as e:
        flash(f'執行檢查時發生錯誤: {str(e)}', 'error')
        print(f"檢查錯誤詳情: {e}")
    
    return redirect(url_for('index') + '?from_loading=true')

@app.route('/loading')
def loading():
    """載入頁面"""
    return render_template('loading.html')

@app.route('/api/status')
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

@app.route('/stress-test/<api_id>')
@login_required
def start_stress_test(api_id):
    """啟動壓力測試"""
    try:
        # 檢查 API 是否存在
        api = data_manager.get_api_by_id(api_id)
        if not api:
            flash('找不到指定的 API', 'error')
            return redirect(url_for('index'))
        
        # 檢查是否已有測試在執行
        if stress_tester.is_test_running(api_id):
            flash(f'API {api["name"]} 的壓力測試正在執行中', 'error')
            return redirect(url_for('index'))
        
        # 在背景執行壓力測試
        def run_test():
            try:
                stress_tester.run_stress_test_sync(api_id)
                print(f"壓力測試完成: {api['name']}")
            except Exception as e:
                print(f"壓力測試錯誤: {e}")
        
        test_thread = threading.Thread(target=run_test, daemon=True)
        test_thread.start()
        
        flash(f'已啟動 API {api["name"]} 的壓力測試', 'success')
        
        # 先顯示loading頁面，然後重定向到實時監控頁面
        return redirect(url_for('loading') + '?redirect=' + url_for('stress_test_live', api_id=api_id) + '&delay=1500')
        
    except Exception as e:
        flash(f'啟動壓力測試時發生錯誤: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/stress-test-live/<api_id>')
@login_required
def stress_test_live(api_id):
    """壓力測試實時監控頁面"""
    api = data_manager.get_api_by_id(api_id)
    if not api:
        flash('找不到指定的 API', 'error')
        return redirect(url_for('index'))
    
    return render_template('stress_live.html', api=api)

@app.route('/stress-test-results/<api_id>')
@login_required
def stress_test_results(api_id):
    """顯示壓力測試結果"""
    api = data_manager.get_api_by_id(api_id)
    if not api:
        flash('找不到指定的 API', 'error')
        return redirect(url_for('index'))
    
    return render_template('stress_results.html', api=api)

@app.route('/api/stress-test-status/<api_id>')
@login_required
def stress_test_status(api_id):
    """取得壓力測試狀態（AJAX 用）"""
    is_running = stress_tester.is_test_running(api_id)
    api = data_manager.get_api_by_id(api_id)
    
    result = {
        'is_running': is_running,
        'api_name': api['name'] if api else 'Unknown'
    }
    
    if api and api.get('stress_test', {}).get('results'):
        latest_result = api['stress_test']['results'][-1]
        result['latest_result'] = {
            'total_requests': latest_result['statistics']['total_requests'],
            'successful_requests': latest_result['statistics']['successful_requests'],
            'failed_requests': latest_result['statistics']['failed_requests'],
            'success_rate': latest_result['statistics']['success_rate'],
            'avg_response_time': latest_result['statistics']['avg_response_time'],
            'min_response_time': latest_result['statistics']['min_response_time'],
            'max_response_time': latest_result['statistics']['max_response_time'],
            'requests_per_second': latest_result['statistics']['requests_per_second'],
            'start_time': latest_result['start_time'],
            'end_time': latest_result.get('end_time'),
            'request_count': len(latest_result['requests']),
            'last_5_requests': [
                {
                    'request_number': i + len(latest_result['requests']) - 4,
                    'success': req.get('success', False),
                    'response_time': req.get('response_time', 0),
                    'status_code': req.get('status_code'),
                    'error': req.get('error'),
                    'timestamp': req.get('timestamp', '')
                }
                for i, req in enumerate(latest_result['requests'][-5:])
            ] if len(latest_result['requests']) > 0 else []
        }
    
    return jsonify(result)

@app.route('/health')
def health_check():
    """應用程式本身的健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'message': 'API Monitor is running (simple version)'
    })

@app.route('/favicon.ico')
def favicon():
    """Favicon 路由避免 404 錯誤"""
    return '', 204

@app.route('/debug-login')
def debug_login():
    """Debug 登入狀態"""
    debug_info = {
        'session': dict(session),
        'user_count': len(user_manager.load_users()),
        'admin_exists': bool(user_manager.get_user_by_username('admin')),
        'current_time': datetime.now().isoformat()
    }
    return f"<pre>{json.dumps(debug_info, indent=2, ensure_ascii=False)}</pre>"

# 用戶管理路由
@app.route('/user-management')
@admin_required
def user_management():
    """用戶管理頁面"""
    users = user_manager.get_all_users()
    stats = user_manager.get_user_stats()
    current_user = user_manager.get_user_by_id(session['user_id'])
    return render_template('user_management.html', users=users, stats=stats, current_user=current_user)

@app.route('/user-management/add', methods=['POST'])
@admin_required
def add_user():
    """新增用戶"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    email = request.form.get('email', '').strip()
    role = request.form.get('role', 'user').strip()
    
    if not username or not password:
        flash('用戶名和密碼不能為空', 'error')
        return redirect(url_for('user_management'))
    
    success, message = user_manager.create_user(username, password, role, email)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('user_management'))

@app.route('/user-management/delete/<user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """刪除用戶"""
    current_user_id = session['user_id']
    success, message = user_manager.delete_user(user_id, current_user_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('user_management'))


@app.route('/projects/delete/<project_name>', methods=['POST'])
@login_required
def delete_project(project_name):
    """刪除專案"""
    try:
        # 檢查專案是否存在
        all_projects = user_story_manager.get_all_projects()
        if project_name not in all_projects:
            flash('找不到指定的專案', 'error')
            return redirect(url_for('test_cases'))
        
        # 獲取該專案的測試案例數量
        test_cases_count = user_story_manager.get_project_test_cases_count(project_name)
        
        # 執行刪除
        success = user_story_manager.delete_project(project_name)
        
        if success:
            if test_cases_count > 0:
                flash(f'成功刪除專案「{project_name}」，已從 {test_cases_count} 個測試案例中移除該專案關聯', 'success')
            else:
                flash(f'成功刪除專案「{project_name}」', 'success')
        else:
            flash('專案刪除失敗', 'error')
    except Exception as e:
        flash(f'刪除專案時發生錯誤: {str(e)}', 'error')
    
    return redirect(url_for('test_cases'))

if __name__ == '__main__':
    print("🚀 啟動 API 監控系統（簡化版）...")
    print("請訪問: http://127.0.0.1:5001 (本機)")
    print("      http://192.168.12.5:5001 (局域網)")
    print("登入頁面: http://192.168.12.5:5001/login")
    print("管理頁面: http://192.168.12.5:5001/admin (需管理員權限)")
    print("用戶管理: http://192.168.12.5:5001/user-management (需管理員權限)")
    print("")
    print("🔧 預設管理員帳號:")
    print("   用戶名: admin")
    print("   密碼: admin123")
    print("")
    print("按 Ctrl+C 停止服務")
    
    # 啟動 Flask 應用程式
    app.run(debug=True, host='0.0.0.0', port=5001)