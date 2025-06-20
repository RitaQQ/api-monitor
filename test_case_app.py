from flask import Flask, request, jsonify, render_template, send_file, session
from datetime import datetime
import json
import os
import csv
import io
import tempfile
from models import TestCase, ProductTag, TestProject, TestResult, TestStatus, ProjectStatus, generate_id
from test_case_manager import TestCaseManager
from report_generator import ReportGenerator
from pdf_exporter import PDFExporter
from user_manager import UserManager

def create_test_case_routes(app: Flask, test_case_manager: TestCaseManager):
    """建立測試案例相關的路由"""
    
    report_generator = ReportGenerator(test_case_manager)
    pdf_exporter = PDFExporter()
    user_manager = UserManager()
    
    # 輔助函數：獲取當前用戶信息
    def get_current_user():
        if 'user_id' in session:
            return user_manager.get_user_by_id(session['user_id'])
        return None
    
    # 檢查是否為管理員
    def is_admin():
        user = get_current_user()
        return user and user.get('role') == 'admin'
    
    # ========== 頁面路由 ==========
    
    @app.route('/test-case-management')
    def test_case_management():
        """測試案例管理頁面"""
        return render_template('test_case_management.html')
    
    @app.route('/test-projects')
    def test_projects():
        """測試專案管理頁面"""
        current_user = get_current_user()
        user_role = current_user.get('role') if current_user else 'guest'
        return render_template('test_projects.html', current_user=current_user, user_role=user_role)
    
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
            # 處理兩種情況：字典列表或物件列表
            if tags:
                # 檢查所有元素是否都有 to_dict 方法
                if all(hasattr(tag, 'to_dict') for tag in tags):
                    return jsonify([tag.to_dict() for tag in tags])
                else:
                    return jsonify(tags)
            else:
                return jsonify([])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/product-tags', methods=['POST'])
    def create_product_tag():
        """建立產品標籤"""
        try:
            data = request.get_json()
            
            # 檢查是否已存在相同名稱
            if test_case_manager.get_product_tag_by_name(data['name']):
                return jsonify({'error': f"產品標籤 '{data['name']}' 已存在"}), 400
            
            tag = test_case_manager.create_product_tag(
                name=data['name'],
                description=data.get('description')
            )
            
            # 處理兩種情況：字典或物件
            if hasattr(tag, 'to_dict'):
                return jsonify(tag.to_dict()), 201
            else:
                return jsonify(tag), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/product-tags/<tag_id>', methods=['GET'])
    def get_product_tag(tag_id):
        """取得特定產品標籤"""
        try:
            tag = test_case_manager.get_product_tag_by_id(int(tag_id))
            if tag:
                # 處理兩種情況：字典或物件
                if hasattr(tag, 'to_dict'):
                    return jsonify(tag.to_dict())
                else:
                    return jsonify(tag)
            else:
                return jsonify({'error': '標籤不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/product-tags/<tag_id>', methods=['PUT'])
    def update_product_tag(tag_id):
        """更新產品標籤"""
        try:
            data = request.get_json()
            success = test_case_manager.update_product_tag(
                tag_id=int(tag_id),
                name=data.get('name'),
                description=data.get('description'),
                color=data.get('color')
            )
            if success:
                # 更新成功，返回更新後的標籤
                updated_tag = test_case_manager.get_product_tag_by_id(int(tag_id))
                if hasattr(updated_tag, 'to_dict'):
                    return jsonify(updated_tag.to_dict())
                else:
                    return jsonify(updated_tag)
            else:
                return jsonify({'error': '更新失敗'}), 400
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
            # 處理兩種情況：字典列表或物件列表
            if cases and hasattr(cases[0], 'to_dict'):
                return jsonify([case.to_dict() for case in cases])
            else:
                return jsonify(cases)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-cases/<case_id>', methods=['GET'])
    def get_test_case(case_id):
        """取得特定測試案例"""
        try:
            case = test_case_manager.get_test_case(case_id)
            if case:
                # 處理兩種情況：字典或物件
                if hasattr(case, 'to_dict'):
                    return jsonify(case.to_dict())
                else:
                    return jsonify(case)
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
            # 處理兩種情況：字典或物件
            if hasattr(case, 'to_dict'):
                return jsonify(case.to_dict()), 201
            else:
                return jsonify(case), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-cases/<case_id>', methods=['PUT'])
    def update_test_case(case_id):
        """更新測試案例"""
        try:
            data = request.get_json()
            case = test_case_manager.update_test_case(case_id, **data)
            if case:
                # 安全檢查：確認物件有 to_dict 方法
                if hasattr(case, 'to_dict'):
                    return jsonify(case.to_dict())
                else:
                    return jsonify(case)
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
            # 處理兩種情況：字典列表或物件列表
            if updated_cases and hasattr(updated_cases[0], 'to_dict'):
                return jsonify([case.to_dict() for case in updated_cases])
            else:
                return jsonify(updated_cases)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========== API 路由 - 測試專案 ==========
    
    @app.route('/api/test-projects', methods=['GET'])
    def get_test_projects():
        """取得所有測試專案"""
        try:
            projects = test_case_manager.get_test_projects()
            # 處理兩種情況：字典列表或物件列表
            if projects:
                # 檢查所有元素是否都有 to_dict 方法
                if all(hasattr(project, 'to_dict') for project in projects):
                    return jsonify([project.to_dict() for project in projects])
                else:
                    return jsonify(projects)
            else:
                return jsonify([])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-projects/<project_id>', methods=['GET'])
    def get_test_project(project_id):
        """取得特定測試專案"""
        try:
            project = test_case_manager.get_test_project_by_id(int(project_id))
            if project:
                # 安全檢查：確認物件有 to_dict 方法
                if hasattr(project, 'to_dict'):
                    return jsonify(project.to_dict())
                else:
                    return jsonify(project)
            else:
                return jsonify({'error': '專案不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-projects', methods=['POST'])
    def create_test_project():
        """建立測試專案"""
        try:
            data = request.get_json()
            
            # 解析開始和結束時間
            start_time = None
            end_time = None
            
            if data.get('start_time'):
                start_time = datetime.fromisoformat(data['start_time']) if isinstance(data['start_time'], str) else data['start_time']
            
            if data.get('end_time'):
                end_time = datetime.fromisoformat(data['end_time']) if isinstance(data['end_time'], str) else data['end_time']
            
            # 驗證負責人用戶是否存在
            responsible_user_input = data.get('responsible_user_id') or data.get('responsible_user')
            responsible_user_id = None
            
            if responsible_user_input:
                from user_manager import UserManager
                user_manager = UserManager()
                
                # 先嘗試用ID查詢，再嘗試用用戶名查詢
                user = user_manager.get_user_by_id(responsible_user_input)
                if user:
                    responsible_user_id = responsible_user_input
                else:
                    # 嘗試用用戶名查詢
                    user = user_manager.get_user_by_username(responsible_user_input)
                    if user:
                        responsible_user_id = user['id']
                    else:
                        return jsonify({'error': f"用戶 '{responsible_user_input}' 不存在"}), 400
            
            project = test_case_manager.create_test_project(
                name=data['name'],
                description=data.get('description'),
                responsible_user_id=responsible_user_id
            )
            # 處理兩種情況：字典或物件
            if hasattr(project, 'to_dict'):
                return jsonify(project.to_dict()), 201
            else:
                return jsonify(project), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-projects/<project_id>', methods=['PUT'])
    def update_test_project(project_id):
        """更新測試專案"""
        try:
            data = request.get_json()
            
            # 處理日期格式
            if 'start_time' in data and isinstance(data['start_time'], str):
                data['start_time'] = datetime.fromisoformat(data['start_time'])
            
            if 'end_time' in data and isinstance(data['end_time'], str):
                data['end_time'] = datetime.fromisoformat(data['end_time'])
            
            # 處理狀態
            if 'status' in data and isinstance(data['status'], str):
                data['status'] = ProjectStatus(data['status'])
            
            success = test_case_manager.update_test_project(int(project_id), **data)
            if success:
                # 更新成功，返回更新後的專案
                updated_project = test_case_manager.get_test_project_by_id(int(project_id))
                if hasattr(updated_project, 'to_dict'):
                    return jsonify(updated_project.to_dict())
                else:
                    return jsonify(updated_project)
            else:
                return jsonify({'error': '更新失敗'}), 400
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
                # 安全檢查：確認物件有 to_dict 方法
                if hasattr(project, 'to_dict'):
                    return jsonify(project.to_dict())
                else:
                    return jsonify(project)
            else:
                return jsonify({'error': '專案不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-projects/<project_id>', methods=['DELETE'])
    def delete_test_project(project_id):
        """刪除測試專案"""
        try:
            success = test_case_manager.delete_test_project(int(project_id))
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
            statistics = test_case_manager.get_project_statistics(int(project_id))
            if statistics:
                # 安全檢查：確認物件有 to_dict 方法
                if hasattr(statistics, 'to_dict'):
                    return jsonify(statistics.to_dict())
                else:
                    return jsonify(statistics)
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
    
    @app.route('/api/test-projects/export-csv', methods=['GET'])
    def export_projects_csv():
        """匯出所有測試專案為CSV"""
        try:
            # 獲取所有專案
            projects = test_case_manager.get_test_projects()
            # 獲取所有測試案例以便查找名稱
            test_cases = test_case_manager.get_test_cases()
            
            # 建立測試案例ID到名稱的映射
            test_case_map = {tc.id: tc.title for tc in test_cases}
            
            # 建立CSV內容
            csv_buffer = io.StringIO()
            csv_writer = csv.writer(csv_buffer)
            
            # CSV標題行
            headers = [
                '專案ID', '專案名稱', '狀態', '開始日期', '結束日期', '負責人', 
                '建立時間', '更新時間', '測試案例ID', '測試案例名稱', 
                '測試狀態', '測試備註', '已知問題', '阻擋原因', '測試時間'
            ]
            csv_writer.writerow(headers)
            
            # 寫入專案和測試結果數據
            for project in projects:
                base_row = [
                    project.id,
                    project.name,
                    project.status.value,
                    project.start_time.strftime('%Y-%m-%d') if project.start_time else '',
                    project.end_time.strftime('%Y-%m-%d') if project.end_time else '',
                    project.responsible_user,
                    project.created_at.strftime('%Y-%m-%d %H:%M:%S') if project.created_at else '',
                    project.updated_at.strftime('%Y-%m-%d %H:%M:%S') if project.updated_at else ''
                ]
                
                # 如果專案有測試案例，為每個測試案例寫一行
                if project.selected_test_cases:
                    for test_case_id in project.selected_test_cases:
                        test_case_name = test_case_map.get(test_case_id, '未知測試案例')
                        test_result = project.test_results.get(test_case_id)
                        
                        if test_result:
                            result_row = base_row + [
                                test_case_id,
                                test_case_name,
                                test_result.status.value,
                                test_result.notes or '',
                                test_result.known_issues or '',
                                test_result.blocked_reason or '',
                                test_result.tested_at.strftime('%Y-%m-%d %H:%M:%S') if test_result.tested_at else ''
                            ]
                        else:
                            result_row = base_row + [
                                test_case_id,
                                test_case_name,
                                '未測試',
                                '', '', '', ''
                            ]
                        csv_writer.writerow(result_row)
                else:
                    # 如果沒有測試案例，只寫專案基本信息
                    empty_row = base_row + ['', '', '', '', '', '', '']
                    csv_writer.writerow(empty_row)
            
            # 準備檔案下載
            csv_content = csv_buffer.getvalue()
            csv_buffer.close()
            
            # 建立檔案名稱
            filename = f"測試專案匯出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # 返回CSV檔案
            return send_file(
                io.BytesIO(csv_content.encode('utf-8-sig')),  # 使用UTF-8 BOM以支援Excel
                mimetype='text/csv',
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
                        'id': user['id'],  # 加入用戶ID
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
            "product_tags": [web_tag['id'], api_tag['id']]
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
            "product_tags": [web_tag['id'], mobile_tag['id']]
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
            "product_tags": [web_tag['id'], api_tag['id'], security_tag['id']]
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
            "product_tags": [security_tag['id'], api_tag['id']]
        }
    ]
    
    for case_data in test_cases_data:
        # 提取並轉換 product_tags
        product_tag_ids = case_data.pop('product_tags', [])
        
        # 創建測試案例，將驗收條件轉換為字串
        test_case = manager.create_test_case(
            title=case_data['title'],
            description=f"用戶角色: {case_data['user_role']}\n功能描述: {case_data['feature_description']}",
            acceptance_criteria='\n'.join(case_data['acceptance_criteria']),
            test_project_id=project['id'],
            product_tag_ids=product_tag_ids
        )
    
    print("✅ 測試案例系統初始化完成")
    return manager