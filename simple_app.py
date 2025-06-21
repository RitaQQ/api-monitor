from flask import Flask, session
from data_manager import DataManager
from api_checker import APIChecker
from stress_tester import StressTester
from user_manager import UserManager
from user_story_manager import UserStoryManager
from test_case_app import create_test_case_routes, init_test_case_data
from config import Config

# 導入路由模組
from routes.auth_routes import register_auth_routes, create_auth_decorators
from routes.main_routes import register_main_routes
from routes.admin_routes import register_admin_routes
from routes.stress_test_routes import register_stress_test_routes
from routes.user_management_routes import register_user_management_routes
from routes.audit_routes import register_audit_routes

import os

def create_app():
    """應用程式工廠函數"""
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
    
    # 模板上下文處理器
    @app.context_processor
    def inject_user():
        """注入用戶信息到所有模板"""
        current_user = None
        if 'user_id' in session:
            current_user = user_manager.get_user_by_id(session['user_id'])
        return dict(current_user=current_user)
    
    # 創建認證裝飾器
    login_required, admin_required = create_auth_decorators(user_manager)
    
    # 註冊所有路由模組
    register_auth_routes(app, user_manager)
    register_main_routes(app, data_manager, api_checker, stress_tester, user_manager, login_required)
    register_admin_routes(app, data_manager, api_checker, admin_required)
    register_stress_test_routes(app, data_manager, stress_tester, login_required)
    register_user_management_routes(app, user_manager, user_story_manager, admin_required, login_required)
    register_audit_routes(app, admin_required)
    
    return app

# 建立應用程式實例
app = create_app()

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