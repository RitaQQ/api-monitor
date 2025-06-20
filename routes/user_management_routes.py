from flask import Blueprint, render_template, request, redirect, url_for, flash, session

# 創建用戶管理功能的藍圖
user_management_bp = Blueprint('user_management', __name__)

def register_user_management_routes(app, user_manager, user_story_manager, admin_required, login_required):
    """註冊用戶管理路由"""
    
    @user_management_bp.route('/user-management')
    @admin_required
    def user_management():
        """用戶管理頁面"""
        users = user_manager.get_all_users()
        stats = user_manager.get_user_stats()
        current_user = user_manager.get_user_by_id(session['user_id'])
        return render_template('user_management.html', users=users, stats=stats, current_user=current_user)

    @user_management_bp.route('/user-management/add', methods=['POST'])
    @admin_required
    def add_user():
        """新增用戶"""
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'user').strip()
        
        if not username or not password:
            flash('用戶名和密碼不能為空', 'error')
            return redirect(url_for('user_management.user_management'))
        
        success, message = user_manager.create_user(username, password, role, email)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        
        return redirect(url_for('user_management.user_management'))

    @user_management_bp.route('/user-management/delete/<user_id>', methods=['POST'])
    @admin_required
    def delete_user(user_id):
        """刪除用戶"""
        current_user_id = session['user_id']
        success, message = user_manager.delete_user(user_id, current_user_id)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        
        return redirect(url_for('user_management.user_management'))

    @user_management_bp.route('/projects/delete/<project_name>', methods=['POST'])
    @admin_required
    def delete_project(project_name):
        """刪除專案"""
        try:
            # 檢查專案是否存在
            all_projects = user_story_manager.get_all_projects()
            if project_name not in all_projects:
                flash('找不到指定的專案', 'error')
                return redirect(url_for('test_cases.test_cases'))
            
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
        
        return redirect(url_for('test_cases.test_cases'))
    
    app.register_blueprint(user_management_bp)