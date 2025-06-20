from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.form_validator import FormValidator

# 創建管理功能的藍圖
admin_bp = Blueprint('admin', __name__)

def register_admin_routes(app, data_manager, api_checker, admin_required):
    """註冊管理功能路由"""
    
    @admin_bp.route('/admin')
    @admin_required
    def admin():
        """管理後台頁面"""
        apis = data_manager.load_apis()
        return render_template('admin.html', apis=apis)

    @admin_bp.route('/admin/add', methods=['POST'])
    @admin_required
    def add_api():
        """新增 API"""
        # 獲取表單數據
        form_data = {
            'name': request.form.get('name', '').strip(),
            'url': request.form.get('url', '').strip(),
            'type': request.form.get('type', 'REST').strip(),
            'method': request.form.get('method', 'GET').strip(),
            'request_body': request.form.get('request_body', '').strip(),
            'concurrent_requests': int(request.form.get('concurrent_requests', 1)),
            'duration_seconds': int(request.form.get('duration_seconds', 10)),
            'interval_seconds': float(request.form.get('interval_seconds', 1.0))
        }
        
        # 驗證表單
        validator = FormValidator()
        is_valid, errors = validator.validate_api_form(form_data, data_manager)
        
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('admin.admin'))
        
        try:
            new_api = data_manager.add_api(
                form_data['name'], form_data['url'], form_data['type'], 
                form_data['method'], form_data['request_body'] if form_data['request_body'] else None,
                form_data['concurrent_requests'], form_data['duration_seconds'], 
                form_data['interval_seconds']
            )
            flash(f'成功新增 API: {form_data["name"]} ({form_data["method"]}) - 壓力測試配置已設定', 'success')
            
            # 立即檢查新增的 API
            try:
                api_checker.check_all_apis()
            except Exception as check_error:
                print(f"檢查 API 時發生錯誤: {check_error}")
            
        except Exception as e:
            flash(f'新增 API 時發生錯誤: {str(e)}', 'error')
        
        return redirect(url_for('admin.admin'))

    @admin_bp.route('/admin/delete/<api_id>', methods=['POST'])
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
        
        return redirect(url_for('admin.admin'))

    @admin_bp.route('/admin/edit/<api_id>')
    @admin_required
    def edit_api(api_id):
        """編輯 API 頁面"""
        api = data_manager.get_api_by_id(api_id)
        if not api:
            flash('找不到指定的 API', 'error')
            return redirect(url_for('admin.admin'))
        return render_template('edit_api.html', api=api)

    @admin_bp.route('/admin/edit/<api_id>', methods=['POST'])
    @admin_required
    def update_api(api_id):
        """更新 API"""
        # 獲取表單數據
        form_data = {
            'name': request.form.get('name', '').strip(),
            'url': request.form.get('url', '').strip(),
            'type': request.form.get('type', 'REST').strip(),
            'method': request.form.get('method', 'GET').strip(),
            'request_body': request.form.get('request_body', '').strip(),
            'concurrent_requests': int(request.form.get('concurrent_requests', 1)),
            'duration_seconds': int(request.form.get('duration_seconds', 10)),
            'interval_seconds': float(request.form.get('interval_seconds', 1.0))
        }
        
        # 驗證表單
        validator = FormValidator()
        is_valid, errors = validator.validate_api_form(form_data, data_manager, api_id)
        
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('admin.edit_api', api_id=api_id))
        
        try:
            success = data_manager.update_api(
                api_id, form_data['name'], form_data['url'], form_data['type'], 
                form_data['method'], form_data['request_body'] if form_data['request_body'] else None,
                form_data['concurrent_requests'], form_data['duration_seconds'], 
                form_data['interval_seconds']
            )
            
            if success:
                flash(f'成功更新 API: {form_data["name"]} ({form_data["method"]})', 'success')
                
                # 立即檢查更新後的 API
                try:
                    api_checker.check_all_apis()
                except Exception as check_error:
                    print(f"檢查 API 時發生錯誤: {check_error}")
                
                return redirect(url_for('admin.admin'))
            else:
                flash('找不到要更新的 API', 'error')
                return redirect(url_for('admin.edit_api', api_id=api_id))
            
        except Exception as e:
            flash(f'更新 API 時發生錯誤: {str(e)}', 'error')
            return redirect(url_for('admin.edit_api', api_id=api_id))
    
    app.register_blueprint(admin_bp)