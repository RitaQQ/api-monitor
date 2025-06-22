from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import threading

# 創建壓力測試功能的藍圖
stress_test_bp = Blueprint('stress_test', __name__)

def register_stress_test_routes(app, data_manager, stress_tester, login_required):
    """註冊壓力測試路由"""
    
    @stress_test_bp.route('/stress-test/<api_id>')
    @login_required
    def start_stress_test(api_id):
        """啟動壓力測試"""
        try:
            # 檢查 API 是否存在
            api = data_manager.get_api_by_id(api_id)
            if not api:
                flash('找不到指定的 API', 'error')
                return redirect(url_for('main.dashboard'))
            
            # 檢查是否已有測試在執行
            if stress_tester.is_test_running(api_id):
                flash(f'API {api["name"]} 的壓力測試正在執行中', 'error')
                return redirect(url_for('main.dashboard'))
            
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
            return redirect(url_for('main.loading') + '?redirect=' + url_for('stress_test.stress_test_live', api_id=api_id) + '&delay=1500')
            
        except Exception as e:
            flash(f'啟動壓力測試時發生錯誤: {str(e)}', 'error')
        
        return redirect(url_for('main.index'))

    @stress_test_bp.route('/stress-test-live/<api_id>')
    @login_required
    def stress_test_live(api_id):
        """壓力測試實時監控頁面"""
        api = data_manager.get_api_by_id(api_id)
        if not api:
            flash('找不到指定的 API', 'error')
            return redirect(url_for('main.index'))
        
        return render_template('stress_live.html', api=api)

    @stress_test_bp.route('/stress-test-results/<api_id>')
    @login_required
    def stress_test_results(api_id):
        """顯示壓力測試結果"""
        api = data_manager.get_api_by_id(api_id)
        if not api:
            flash('找不到指定的 API', 'error')
            return redirect(url_for('main.index'))
        
        return render_template('stress_results.html', api=api)

    @stress_test_bp.route('/api/stress-test-status/<api_id>')
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
    
    app.register_blueprint(stress_test_bp)