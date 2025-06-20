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
    
    # 輔助函數：將後端資料格式轉換為前端期望格式
    def _process_case_for_frontend(case_dict):
        """將後端測試案例資料轉換為前端期望格式"""
        processed_case = case_dict.copy()
        
        # 將 description 拆分為 user_role 和 feature_description
        description = case_dict.get('description', '')
        user_role = ''
        feature_description = ''
        
        if description:
            lines = description.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('用戶角色:'):
                    user_role = line.replace('用戶角色:', '').strip()
                elif line.startswith('功能描述:'):
                    feature_description = line.replace('功能描述:', '').strip()
                elif not user_role and not feature_description:
                    # 如果沒有特定格式，將整個描述作為功能描述
                    feature_description = description
        
        processed_case['user_role'] = user_role
        processed_case['feature_description'] = feature_description
        
        # 將 acceptance_criteria 字串轉換為列表
        if processed_case.get('acceptance_criteria'):
            if isinstance(processed_case['acceptance_criteria'], str):
                processed_case['acceptance_criteria'] = [
                    criterion.strip() 
                    for criterion in processed_case['acceptance_criteria'].split('\n') 
                    if criterion.strip()
                ]
        else:
            processed_case['acceptance_criteria'] = []
        
        # 添加空的 test_notes 欄位（前端期望）
        processed_case['test_notes'] = ''
        
        # 確保 product_tags 是 ID 陣列格式
        if 'product_tags' in processed_case:
            if isinstance(processed_case['product_tags'], list) and processed_case['product_tags']:
                # 如果是物件陣列，轉換為 ID 陣列
                if isinstance(processed_case['product_tags'][0], dict):
                    processed_case['product_tags'] = [tag['id'] for tag in processed_case['product_tags']]
        else:
            processed_case['product_tags'] = []
        
        return processed_case
    
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
            if cases:
                # 轉換後端資料格式為前端期望格式
                processed_cases = []
                for case in cases:
                    if hasattr(case, 'to_dict'):
                        case_dict = case.to_dict()
                    else:
                        case_dict = case
                    
                    # 將 description 拆分為 user_role 和 feature_description
                    processed_case = _process_case_for_frontend(case_dict)
                    processed_cases.append(processed_case)
                
                return jsonify(processed_cases)
            else:
                return jsonify([])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-cases/<case_id>', methods=['GET'])
    def get_test_case(case_id):
        """取得特定測試案例"""
        try:
            case = test_case_manager.get_test_case_by_id(int(case_id))
            if case:
                # 處理兩種情況：字典或物件
                if hasattr(case, 'to_dict'):
                    case_dict = case.to_dict()
                else:
                    case_dict = case
                
                # 將後端資料格式轉換為前端期望格式
                processed_case = _process_case_for_frontend(case_dict)
                return jsonify(processed_case)
            else:
                return jsonify({'error': '測試案例不存在'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-cases', methods=['POST'])
    def create_test_case():
        """建立測試案例"""
        try:
            data = request.get_json()
            
            # 處理前端資料格式轉換
            # 合併 user_role 和 feature_description 為 description
            description = None
            if data.get('user_role') or data.get('feature_description'):
                user_role = data.get('user_role', '').strip()
                feature_desc = data.get('feature_description', '').strip()
                if user_role and feature_desc:
                    description = f"用戶角色: {user_role}\n功能描述: {feature_desc}"
                elif feature_desc:
                    description = feature_desc
                elif user_role:
                    description = f"用戶角色: {user_role}"
            else:
                description = data.get('description')
            
            # 處理驗收條件：如果是列表則轉換為字符串
            acceptance_criteria = data.get('acceptance_criteria')
            if isinstance(acceptance_criteria, list):
                acceptance_criteria = '\n'.join(acceptance_criteria) if acceptance_criteria else None
            
            # 處理產品標籤：前端可能發送 product_tags 或 product_tag_ids
            product_tag_ids = data.get('product_tag_ids') or data.get('product_tags') or []
            
            case = test_case_manager.create_test_case(
                title=data['title'],
                description=description,
                acceptance_criteria=acceptance_criteria,
                priority=data.get('priority', 'medium'),
                status=data.get('status', 'draft'),
                test_project_id=data.get('test_project_id'),
                responsible_user_id=data.get('responsible_user_id'),
                estimated_hours=data.get('estimated_hours', 0),
                product_tag_ids=product_tag_ids
            )
            # 處理兩種情況：字典或物件
            if hasattr(case, 'to_dict'):
                case_dict = case.to_dict()
            else:
                case_dict = case
            
            # 將後端資料格式轉換為前端期望格式
            processed_case = _process_case_for_frontend(case_dict)
            return jsonify(processed_case), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-cases/<case_id>', methods=['PUT'])
    def update_test_case(case_id):
        """更新測試案例"""
        try:
            data = request.get_json()
            
            # 處理前端資料格式轉換
            # 合併 user_role 和 feature_description 為 description
            if data.get('user_role') or data.get('feature_description'):
                user_role = data.get('user_role', '').strip()
                feature_desc = data.get('feature_description', '').strip()
                if user_role and feature_desc:
                    data['description'] = f"用戶角色: {user_role}\n功能描述: {feature_desc}"
                elif feature_desc:
                    data['description'] = feature_desc
                elif user_role:
                    data['description'] = f"用戶角色: {user_role}"
                # 移除前端專用欄位
                data.pop('user_role', None)
                data.pop('feature_description', None)
            
            # 處理驗收條件：如果是列表則轉換為字符串
            if 'acceptance_criteria' in data and isinstance(data['acceptance_criteria'], list):
                data['acceptance_criteria'] = '\n'.join(data['acceptance_criteria']) if data['acceptance_criteria'] else None
            
            # 處理產品標籤：前端可能發送 product_tags 或 product_tag_ids
            if 'product_tags' in data:
                data['product_tag_ids'] = data.pop('product_tags')
            
            # 移除前端專用欄位
            data.pop('test_notes', None)  # 這個欄位在後端沒有對應
            
            success = test_case_manager.update_test_case(int(case_id), **data)
            if success:
                # 更新成功，返回更新後的案例
                updated_case = test_case_manager.get_test_case_by_id(int(case_id))
                if hasattr(updated_case, 'to_dict'):
                    case_dict = updated_case.to_dict()
                else:
                    case_dict = updated_case
                
                # 將後端資料格式轉換為前端期望格式
                processed_case = _process_case_for_frontend(case_dict)
                return jsonify(processed_case)
            else:
                return jsonify({'error': '更新失敗'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/test-cases/<case_id>', methods=['DELETE'])
    def delete_test_case(case_id):
        """刪除測試案例"""
        try:
            success = test_case_manager.delete_test_case(int(case_id))
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
                responsible_user_id=responsible_user_id,
                start_time=data.get('start_time'),
                end_time=data.get('end_time')
            )
            
            # 處理選中的測試案例關聯
            selected_test_cases = data.get('selected_test_cases', [])
            if selected_test_cases and project:
                project_id = project['id']
                for case_id in selected_test_cases:
                    try:
                        test_case_manager.update_test_case(int(case_id), test_project_id=project_id)
                    except Exception as e:
                        print(f"關聯測試案例 {case_id} 失敗: {e}")
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
            
            # 處理測試案例關聯（需要單獨處理，不能傳給 update_test_project）
            selected_test_cases = data.pop('selected_test_cases', None)
            
            # update_test_project 現在支援時間欄位
            allowed_fields = ['name', 'description', 'status', 'responsible_user_id', 'start_time', 'end_time']
            filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
            
            success = test_case_manager.update_test_project(int(project_id), **filtered_data)
            
            # 處理測試案例關聯更新
            if success and selected_test_cases is not None:
                # 先清除該專案的所有測試案例關聯
                try:
                    test_case_manager.clear_project_test_cases(int(project_id))
                    # 重新關聯選中的測試案例
                    for case_id in selected_test_cases:
                        test_case_manager.update_test_case(int(case_id), test_project_id=int(project_id))
                except Exception as e:
                    print(f"更新測試案例關聯失敗: {e}")
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
            
            # 建立測試案例ID到名稱的映射（修復：使用字典語法）
            test_case_map = {tc['id']: tc['title'] for tc in test_cases}
            
            # 建立CSV內容
            csv_buffer = io.StringIO()
            csv_writer = csv.writer(csv_buffer)
            
            # CSV標題行
            headers = [
                '專案ID', '專案名稱', '狀態', '描述', '負責人', 
                '建立時間', '更新時間', '測試案例ID', '測試案例名稱'
            ]
            csv_writer.writerow(headers)
            
            # 寫入專案數據（修復：使用字典語法）
            for project in projects:
                # 解析時間字串
                created_at = project.get('created_at', '')
                updated_at = project.get('updated_at', '')
                
                # 格式化時間（如果是datetime物件則轉字串，如果已是字串則直接使用）
                if hasattr(created_at, 'strftime'):
                    created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    created_at_str = str(created_at) if created_at else ''
                
                if hasattr(updated_at, 'strftime'):
                    updated_at_str = updated_at.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    updated_at_str = str(updated_at) if updated_at else ''
                
                base_row = [
                    project['id'],
                    project['name'],
                    project.get('status', ''),
                    project.get('description', ''),
                    project.get('responsible_user_name', ''),
                    created_at_str,
                    updated_at_str
                ]
                
                # 獲取專案關聯的測試案例
                project_cases = test_case_manager.get_test_cases(project_id=project['id'])
                
                if project_cases:
                    # 為每個測試案例寫一行
                    for test_case in project_cases:
                        result_row = base_row + [
                            test_case['id'],
                            test_case['title']
                        ]
                        csv_writer.writerow(result_row)
                else:
                    # 如果沒有測試案例，只寫專案基本信息
                    empty_row = base_row + ['', '']
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
                    # 構建簡潔的顯示名稱（僅用戶名稱）
                    role = user.get('role', 'user')
                    
                    active_users.append({
                        'id': user['id'],  # 加入用戶ID
                        'username': user['username'],
                        'display_name': user['username'],  # 簡化顯示為用戶名稱
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