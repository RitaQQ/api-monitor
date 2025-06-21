from flask import request, render_template, jsonify, make_response, session
from audit_logger import AuditLogger
from datetime import datetime, timedelta
import csv
import io


def register_audit_routes(app, admin_required):
    """註冊操作記錄路由"""
    
    @app.route('/audit-logs')
    @admin_required
    def audit_logs():
        """操作記錄頁面（僅管理員可查看）"""
        # 獲取篩選參數
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        action = request.args.get('action', '')
        resource_type = request.args.get('resource_type', '')
        username = request.args.get('username', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        export = request.args.get('export', '')
        
        # 計算偏移量
        offset = (page - 1) * per_page
        
        # 構建篩選條件
        filters = {}
        if action:
            filters['action'] = action
        if resource_type:
            filters['resource_type'] = resource_type
        if username:
            filters['username'] = username
        if start_date:
            filters['start_date'] = start_date + ' 00:00:00'
        if end_date:
            filters['end_date'] = end_date + ' 23:59:59'
        
        # 如果是匯出請求
        if export == 'csv':
            return export_audit_logs_csv(filters)
        
        # 獲取操作記錄
        logs = AuditLogger.get_audit_logs(
            limit=per_page,
            offset=offset,
            **filters
        )
        
        # 獲取總數（用於分頁）
        total_logs = AuditLogger.get_audit_logs(limit=9999, offset=0, **filters)
        total = len(total_logs)
        
        # 獲取統計信息
        stats = get_audit_stats()
        
        # 分頁信息
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': page * per_page < total,
            'prev_num': page - 1 if page > 1 else None,
            'next_num': page + 1 if page * per_page < total else None
        }
        
        # 添加分頁迭代器
        pagination['iter_pages'] = lambda: get_pagination_pages(page, pagination['pages'])
        
        return render_template('audit_logs.html',
                             logs=logs,
                             stats=stats,
                             pagination=pagination)
    
    @app.route('/api/audit-logs')
    @admin_required
    def api_audit_logs():
        """API端點獲取操作記錄（JSON格式）"""
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        action = request.args.get('action', '')
        resource_type = request.args.get('resource_type', '')
        username = request.args.get('username', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        filters = {}
        if action:
            filters['action'] = action
        if resource_type:
            filters['resource_type'] = resource_type
        if username:
            filters['username'] = username
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        
        logs = AuditLogger.get_audit_logs(
            limit=limit,
            offset=offset,
            **filters
        )
        
        return jsonify({
            'logs': logs,
            'stats': get_audit_stats()
        })
    
    @app.route('/api/test-case-audit-logs')
    @admin_required
    def api_test_case_audit_logs():
        """API端點獲取測試案例相關操作記錄"""
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        action = request.args.get('action', '')
        username = request.args.get('username', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        filters = {
            'resource_type': 'TEST_CASE'  # 只顯示測試案例相關記錄
        }
        
        if action:
            filters['action'] = action
        if username:
            filters['username'] = username
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        
        logs = AuditLogger.get_audit_logs(
            limit=limit,
            offset=offset,
            **filters
        )
        
        # 獲取測試案例專用統計
        test_case_stats = get_test_case_audit_stats()
        
        return jsonify({
            'logs': logs,
            'stats': test_case_stats,
            'total': len(logs)
        })
    
    @app.route('/api/test-project-audit-logs')
    @admin_required
    def api_test_project_audit_logs():
        """API端點獲取測試專案相關操作記錄"""
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        action = request.args.get('action', '')
        username = request.args.get('username', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        filters = {
            'resource_type': 'TEST_PROJECT'  # 只顯示測試專案相關記錄
        }
        
        if action:
            filters['action'] = action
        if username:
            filters['username'] = username
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        
        logs = AuditLogger.get_audit_logs(
            limit=limit,
            offset=offset,
            **filters
        )
        
        # 獲取測試專案專用統計
        test_project_stats = get_test_project_audit_stats()
        
        return jsonify({
            'logs': logs,
            'stats': test_project_stats,
            'total': len(logs)
        })


def export_audit_logs_csv(filters):
    """匯出操作記錄為CSV"""
    # 獲取所有符合條件的記錄
    logs = AuditLogger.get_audit_logs(limit=10000, offset=0, **filters)
    
    # 創建CSV文件
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 寫入標題行
    headers = [
        '時間', '用戶名', '操作類型', '資源類型', '資源名稱', 
        'IP地址', '瀏覽器', '變更前', '變更後'
    ]
    writer.writerow(headers)
    
    # 寫入數據行
    for log in logs:
        old_values = str(log.get('old_values', '')) if log.get('old_values') else ''
        new_values = str(log.get('new_values', '')) if log.get('new_values') else ''
        
        row = [
            log.get('created_at', ''),
            log.get('username', ''),
            log.get('action', ''),
            log.get('resource_type', ''),
            log.get('resource_name', ''),
            log.get('ip_address', ''),
            log.get('user_agent', ''),
            old_values,
            new_values
        ]
        writer.writerow(row)
    
    # 創建響應
    output.seek(0)
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'audit_logs_{timestamp}.csv'
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response


def get_audit_stats():
    """獲取操作記錄統計信息"""
    from database.db_manager import db_manager
    
    # 總記錄數
    total_query = "SELECT COUNT(*) as count FROM audit_logs"
    total_result = db_manager.execute_query(total_query)
    total = total_result[0]['count'] if total_result else 0
    
    # 今日操作數
    today = datetime.now().strftime('%Y-%m-%d')
    today_query = """
        SELECT COUNT(*) as count 
        FROM audit_logs 
        WHERE DATE(created_at) = ?
    """
    today_result = db_manager.execute_query(today_query, (today,))
    today_count = today_result[0]['count'] if today_result else 0
    
    # 活躍用戶數（最近7天）
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    users_query = """
        SELECT COUNT(DISTINCT user_id) as count 
        FROM audit_logs 
        WHERE DATE(created_at) >= ?
    """
    users_result = db_manager.execute_query(users_query, (week_ago,))
    unique_users = users_result[0]['count'] if users_result else 0
    
    # 關鍵操作數（創建、更新、刪除）
    critical_query = """
        SELECT COUNT(*) as count 
        FROM audit_logs 
        WHERE action IN ('CREATE', 'UPDATE', 'DELETE')
        AND DATE(created_at) = ?
    """
    critical_result = db_manager.execute_query(critical_query, (today,))
    critical_actions = critical_result[0]['count'] if critical_result else 0
    
    return {
        'total': total,
        'today_count': today_count,
        'unique_users': unique_users,
        'critical_actions': critical_actions
    }


def get_test_case_audit_stats():
    """獲取測試案例專用操作記錄統計信息"""
    from database.db_manager import db_manager
    
    # 測試案例總操作數
    total_query = """
        SELECT COUNT(*) as count 
        FROM audit_logs 
        WHERE resource_type = 'TEST_CASE'
    """
    total_result = db_manager.execute_query(total_query)
    total = total_result[0]['count'] if total_result else 0
    
    # 今日測試案例操作數
    today = datetime.now().strftime('%Y-%m-%d')
    today_query = """
        SELECT COUNT(*) as count 
        FROM audit_logs 
        WHERE resource_type = 'TEST_CASE' AND DATE(created_at) = ?
    """
    today_result = db_manager.execute_query(today_query, (today,))
    today_count = today_result[0]['count'] if today_result else 0
    
    # 按操作類型統計測試案例操作
    action_query = """
        SELECT action, COUNT(*) as count 
        FROM audit_logs 
        WHERE resource_type = 'TEST_CASE'
        GROUP BY action
        ORDER BY count DESC
    """
    action_result = db_manager.execute_query(action_query)
    
    # 最近活躍的測試案例編輯者（最近7天）
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    editors_query = """
        SELECT COUNT(DISTINCT user_id) as count 
        FROM audit_logs 
        WHERE resource_type = 'TEST_CASE' 
        AND DATE(created_at) >= ?
        AND action IN ('CREATE', 'UPDATE', 'DELETE')
    """
    editors_result = db_manager.execute_query(editors_query, (week_ago,))
    active_editors = editors_result[0]['count'] if editors_result else 0
    
    return {
        'total_test_case_operations': total,
        'today_test_case_operations': today_count,
        'active_editors': active_editors,
        'operations_by_action': action_result
    }


def get_test_project_audit_stats():
    """獲取測試專案專用操作記錄統計信息"""
    from database.db_manager import db_manager
    
    # 測試專案總操作數
    total_query = """
        SELECT COUNT(*) as count 
        FROM audit_logs 
        WHERE resource_type = 'TEST_PROJECT'
    """
    total_result = db_manager.execute_query(total_query)
    total = total_result[0]['count'] if total_result else 0
    
    # 今日測試專案操作數
    today = datetime.now().strftime('%Y-%m-%d')
    today_query = """
        SELECT COUNT(*) as count 
        FROM audit_logs 
        WHERE resource_type = 'TEST_PROJECT' AND DATE(created_at) = ?
    """
    today_result = db_manager.execute_query(today_query, (today,))
    today_count = today_result[0]['count'] if today_result else 0
    
    # 按操作類型統計測試專案操作
    action_query = """
        SELECT action, COUNT(*) as count 
        FROM audit_logs 
        WHERE resource_type = 'TEST_PROJECT'
        GROUP BY action
        ORDER BY count DESC
    """
    action_result = db_manager.execute_query(action_query)
    
    # 最近活躍的測試專案管理者（最近7天）
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    managers_query = """
        SELECT COUNT(DISTINCT user_id) as count 
        FROM audit_logs 
        WHERE resource_type = 'TEST_PROJECT' 
        AND DATE(created_at) >= ?
        AND action IN ('CREATE', 'UPDATE', 'DELETE')
    """
    managers_result = db_manager.execute_query(managers_query, (week_ago,))
    active_managers = managers_result[0]['count'] if managers_result else 0
    
    # 最近創建的專案數（最近30天）
    month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_projects_query = """
        SELECT COUNT(*) as count 
        FROM audit_logs 
        WHERE resource_type = 'TEST_PROJECT' 
        AND action = 'CREATE'
        AND DATE(created_at) >= ?
    """
    recent_projects_result = db_manager.execute_query(recent_projects_query, (month_ago,))
    recent_projects = recent_projects_result[0]['count'] if recent_projects_result else 0
    
    return {
        'total_test_project_operations': total,
        'today_test_project_operations': today_count,
        'active_managers': active_managers,
        'recent_projects_created': recent_projects,
        'operations_by_action': action_result
    }


def get_pagination_pages(current_page, total_pages, window=5):
    """生成分頁頁碼列表"""
    if total_pages <= window:
        return list(range(1, total_pages + 1))
    
    start = max(1, current_page - window // 2)
    end = min(total_pages, start + window - 1)
    
    if end - start < window - 1:
        start = max(1, end - window + 1)
    
    pages = list(range(start, end + 1))
    
    # 添加省略號
    result = []
    if start > 1:
        result.append(1)
        if start > 2:
            result.append(None)  # 省略號
    
    result.extend(pages)
    
    if end < total_pages:
        if end < total_pages - 1:
            result.append(None)  # 省略號
        result.append(total_pages)
    
    return result