from flask import Flask, request, jsonify, render_template, send_file
from datetime import datetime
import json
import os
from models import TestCase, ProductTag, TestProject, TestResult, TestStatus, ProjectStatus, generate_id
from test_case_manager import TestCaseManager
from report_generator import ReportGenerator
from pdf_exporter import PDFExporter
from user_manager import UserManager
import io
import tempfile

def create_test_case_routes(app: Flask, test_case_manager: TestCaseManager):
    """建立測試案例相關的路由"""
    
    report_generator = ReportGenerator(test_case_manager)
    pdf_exporter = PDFExporter()
    user_manager = UserManager()
    
    # ========== 頁面路由 ==========
    
    @app.route('/test-case-management')
    def test_case_management():
        """測試案例管理頁面"""
        return render_template('test_case_management.html')
    
    @app.route('/test-projects')
    def test_projects():
        """測試專案管理頁面"""
        return render_template('test_projects.html')
    
    @app.route('/test-projects/<project_id>')
    def project_detail(project_id):
        """測試專案詳情頁面"""
        return render_template('project_detail.html', project_id=project_id)
    
    @app.route('/product-tag-management')
    def product_tag_management():
        """產品標籤管理頁面"""
        return render_template('product_tag_management.html')
    
    # ========== API 路由 - 產品標籤 ==========
    
    @app.route('/api/product-tags', methods=['GET'])
    def get_product_tags():
        """取得所有產品標籤"""
        try:
            tags = test_case_manager.get_product_tags()
            return jsonify([tag.to_dict() for tag in tags])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/product-tags', methods=['POST'])
    def create_product_tag():
        """建立產品標籤"""
        try:
            data = request.get_json()
            tag = test_case_manager.create_product_tag(
                name=data['name'],
                description=data.get('description')
            )
            return jsonify(tag.to_dict()), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/product-tags/<tag_id>', methods=['PUT'])
    def update_product_tag(tag_id):
        """更新產品標籤"""
        try:
            data = request.get_json()
            tag = test_case_manager.update_product_tag(
                tag_id=tag_id,
                name=data.get('name'),
                description=data.get('description')
            )
            if tag:
                return jsonify(tag.to_dict())
            else:
                return jsonify({'error': '標籤不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/product-tags/<tag_id>', methods=['DELETE'])
    def delete_product_tag(tag_id):
        """刪除產品標籤"""
        try:
            success = test_case_manager.delete_product_tag(tag_id)
            if success:
                return jsonify({'message': '刪除成功'})
            else:
                return jsonify({'error': '標籤不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== API 路由 - 測試案例 ==========
    
    @app.route('/api/test-cases', methods=['GET'])
    def get_test_cases():
        """取得所有測試案例"""
        try:
            cases = test_case_manager.get_test_cases()
            return jsonify([case.to_dict() for case in cases])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-cases/<case_id>', methods=['GET'])
    def get_test_case(case_id):
        """取得特定測試案例"""
        try:
            case = test_case_manager.get_test_case(case_id)
            if case:
                return jsonify(case.to_dict())
            else:
                return jsonify({'error': '測試案例不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-cases', methods=['POST'])
    def create_test_case():
        """建立測試案例"""
        try:
            data = request.get_json()
            case = test_case_manager.create_test_case(
                title=data['title'],
                user_role=data['user_role'],
                feature_description=data['feature_description'],
                acceptance_criteria=data.get('acceptance_criteria', []),
                test_notes=data.get('test_notes'),
                product_tags=data.get('product_tags', [])
            )
            return jsonify(case.to_dict()), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-cases/<case_id>', methods=['PUT'])
    def update_test_case(case_id):
        """更新測試案例"""
        try:
            data = request.get_json()
            case = test_case_manager.update_test_case(case_id, **data)
            if case:
                return jsonify(case.to_dict())
            else:
                return jsonify({'error': '測試案例不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-cases/<case_id>', methods=['DELETE'])
    def delete_test_case(case_id):
        """刪除測試案例"""
        try:
            success = test_case_manager.delete_test_case(case_id)
            if success:
                return jsonify({'message': '刪除成功'})
            else:
                return jsonify({'error': '測試案例不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-cases/batch', methods=['PUT'])
    def batch_update_test_cases():
        """批量更新測試案例"""
        try:
            data = request.get_json()
            updates = data.get('updates', [])
            updated_cases = test_case_manager.batch_update_test_cases(updates)
            return jsonify([case.to_dict() for case in updated_cases])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== API 路由 - 測試專案 ==========
    
    @app.route('/api/test-projects', methods=['GET'])
    def get_test_projects():
        """取得所有測試專案"""
        try:
            projects = test_case_manager.get_test_projects()
            return jsonify([project.to_dict() for project in projects])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-projects/<project_id>', methods=['GET'])
    def get_test_project(project_id):
        """取得特定測試專案"""
        try:
            project = test_case_manager.get_test_project(project_id)
            if project:
                return jsonify(project.to_dict())
            else:
                return jsonify({'error': '專案不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-projects', methods=['POST'])
    def create_test_project():
        """建立測試專案"""
        try:
            data = request.get_json()
            test_date = datetime.fromisoformat(data['test_date']) if isinstance(data['test_date'], str) else data['test_date']
            
            project = test_case_manager.create_test_project(
                name=data['name'],
                test_date=test_date,
                responsible_user=data['responsible_user'],
                selected_test_cases=data['selected_test_cases']
            )
            return jsonify(project.to_dict()), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-projects/<project_id>', methods=['PUT'])
    def update_test_project(project_id):
        """更新測試專案"""
        try:
            data = request.get_json()
            
            # 處理日期格式
            if 'test_date' in data and isinstance(data['test_date'], str):
                data['test_date'] = datetime.fromisoformat(data['test_date'])
            
            # 處理狀態
            if 'status' in data and isinstance(data['status'], str):
                data['status'] = ProjectStatus(data['status'])
            
            project = test_case_manager.update_test_project(project_id, **data)
            if project:
                return jsonify(project.to_dict())
            else:
                return jsonify({'error': '專案不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-projects/<project_id>/results', methods=['PUT'])
    def update_test_result(project_id):
        """更新測試結果"""
        try:
            data = request.get_json()
            
            project = test_case_manager.update_test_result(
                project_id=project_id,
                test_case_id=data['test_case_id'],
                status=TestStatus(data['status']),
                notes=data.get('notes'),
                known_issues=data.get('known_issues'),
                blocked_reason=data.get('blocked_reason')
            )
            
            if project:
                return jsonify(project.to_dict())
            else:
                return jsonify({'error': '專案不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-projects/<project_id>', methods=['DELETE'])
    def delete_test_project(project_id):
        """刪除測試專案"""
        try:
            success = test_case_manager.delete_test_project(project_id)
            if success:
                return jsonify({'message': '刪除成功'})
            else:
                return jsonify({'error': '專案不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== API 路由 - 統計和報告 ==========
    
    @app.route('/api/test-projects/<project_id>/statistics', methods=['GET'])
    def get_project_statistics(project_id):
        """取得專案統計"""
        try:
            statistics = test_case_manager.get_project_statistics(project_id)
            if statistics:
                return jsonify(statistics.to_dict())
            else:
                return jsonify({'error': '專案不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-projects/<project_id>/report', methods=['GET'])
    def get_project_report(project_id):
        """取得專案報告"""
        try:
            report = report_generator.generate_project_report(project_id)
            if report:
                return jsonify(report_generator.export_to_dict(report))
            else:
                return jsonify({'error': '專案不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-projects/<project_id>/export-pdf', methods=['POST'])
    def export_project_pdf(project_id):
        """匯出專案PDF報告"""
        try:
            report = report_generator.generate_project_report(project_id)
            if not report:
                return jsonify({'error': '專案不存在'}), 404
            
            # 生成PDF
            pdf_data = pdf_exporter.export_project_report(report)
            
            # 建立檔案名稱
            filename = f"{report.project.name}_測試報告_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            # 返回PDF檔案
            return send_file(
                io.BytesIO(pdf_data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== API 路由 - 用戶管理 ==========
    
    @app.route('/api/users', methods=['GET'])
    def get_users():
        """取得所有用戶（用於專案負責人選擇）"""
        try:
            # 從用戶管理系統獲取真實用戶列表
            all_users = user_manager.get_all_users()
            
            # 只返回活躍用戶，並格式化為前端需要的格式
            active_users = []
            for user in all_users:
                if user.get('is_active', True):  # 只包含活躍用戶
                    # 構建顯示名稱
                    display_name = user.get('email', user['username'])
                    
                    # 根據角色添加標識
                    role = user.get('role', 'user')
                    if role == 'admin':
                        display_name = f"👑 {display_name} (管理員)"
                    else:
                        display_name = f"👤 {display_name} (用戶)"
                    
                    active_users.append({
                        'username': user['username'],
                        'display_name': display_name,
                        'role': role,
                        'email': user.get('email', ''),
                        'created_at': user.get('created_at', '')
                    })
            
            # 按角色排序：管理員在前，然後按用戶名排序
            active_users.sort(key=lambda u: (u['role'] != 'admin', u['username']))
            
            return jsonify(active_users)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def init_test_case_data():
    """初始化測試案例系統的示例資料"""
    manager = TestCaseManager()
    
    # 檢查是否已有資料
    if manager.get_test_cases() or manager.get_product_tags():
        return manager
    
    # 建立示例產品標籤
    web_tag = manager.create_product_tag("Web前端", "網頁前端功能測試")
    api_tag = manager.create_product_tag("API後端", "後端API介面測試")
    mobile_tag = manager.create_product_tag("行動裝置", "手機App測試")
    security_tag = manager.create_product_tag("資訊安全", "安全性相關測試")
    
    # 建立示例測試案例
    test_cases_data = [
        {
            "title": "用戶登入功能",
            "user_role": "作為一位註冊用戶",
            "feature_description": "我希望能夠使用帳號密碼登入系統",
            "acceptance_criteria": [
                "輸入正確的帳號密碼能成功登入",
                "輸入錯誤的帳號密碼會顯示錯誤訊息",
                "登入成功後會跳轉到首頁"
            ],
            "test_notes": "需要測試各種邊界條件和錯誤情況",
            "product_tags": [web_tag.id, api_tag.id]
        },
        {
            "title": "商品搜尋功能",
            "user_role": "作為一位購物者",
            "feature_description": "我希望能夠搜尋我想要的商品",
            "acceptance_criteria": [
                "輸入關鍵字能夠找到相關商品",
                "搜尋結果能夠按相關度排序",
                "能夠使用篩選條件縮小搜尋範圍"
            ],
            "test_notes": "需要測試搜尋性能和準確度",
            "product_tags": [web_tag.id, mobile_tag.id]
        },
        {
            "title": "訂單結帳流程",
            "user_role": "作為一位已登入的購物者",
            "feature_description": "我希望能夠完成商品結帳流程",
            "acceptance_criteria": [
                "能夠選擇配送方式",
                "能夠選擇付款方式",
                "訂單確認後會收到確認郵件"
            ],
            "test_notes": "需要測試各種付款方式的整合",
            "product_tags": [web_tag.id, api_tag.id, security_tag.id]
        },
        {
            "title": "用戶資料安全",
            "user_role": "作為一位系統管理員",
            "feature_description": "我希望確保用戶資料的安全性",
            "acceptance_criteria": [
                "密碼需要加密存儲",
                "敏感資料需要HTTPS傳輸",
                "需要防範SQL注入攻擊"
            ],
            "test_notes": "使用安全掃描工具進行測試",
            "product_tags": [security_tag.id, api_tag.id]
        }
    ]
    
    for case_data in test_cases_data:
        manager.create_test_case(**case_data)
    
    print("✅ 測試案例系統初始化完成")
    return manager