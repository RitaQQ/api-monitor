from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from data_manager import DataManager
from api_checker import APIChecker
from stress_tester import StressTester
from config import Config
import os
import threading

app = Flask(__name__)
config = Config()
app.config.from_object(config)

# 初始化組件
data_manager = DataManager(config.DATA_FILE)
api_checker = APIChecker(data_manager)
stress_tester = StressTester(data_manager)

@app.route('/')
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
    
    return render_template('index.html', apis=apis, stats=stats)

@app.route('/admin')
def admin():
    """管理後台頁面"""
    apis = data_manager.load_apis()
    return render_template('admin.html', apis=apis)

@app.route('/admin/add', methods=['POST'])
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

@app.route('/check-now')
def check_now():
    """立即執行檢查"""
    try:
        api_checker.check_all_apis()
        flash('已執行立即檢查', 'success')
    except Exception as e:
        flash(f'執行檢查時發生錯誤: {str(e)}', 'error')
        print(f"檢查錯誤詳情: {e}")
    
    return redirect(url_for('index'))

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
        
    except Exception as e:
        flash(f'啟動壓力測試時發生錯誤: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/stress-test-results/<api_id>')
def stress_test_results(api_id):
    """顯示壓力測試結果"""
    api = data_manager.get_api_by_id(api_id)
    if not api:
        flash('找不到指定的 API', 'error')
        return redirect(url_for('index'))
    
    return render_template('stress_results.html', api=api)

@app.route('/api/stress-test-status/<api_id>')
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
        result['latest_result'] = latest_result
    
    return jsonify(result)

@app.route('/health')
def health_check():
    """應用程式本身的健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'message': 'API Monitor is running (simple version)'
    })

if __name__ == '__main__':
    print("🚀 啟動 API 監控系統（簡化版）...")
    print("請訪問: http://127.0.0.1:3000")
    print("管理頁面: http://127.0.0.1:3000/admin")
    print("按 Ctrl+C 停止服務")
    
    # 啟動 Flask 應用程式
    app.run(debug=True, host='127.0.0.1', port=3000)