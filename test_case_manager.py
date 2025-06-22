import json
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import logging
import sys
from database.db_manager import db_manager

# 配置詳細的日誌輸出
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# 創建專門的 logger
db_logger = logging.getLogger('test_case_db')
db_logger.setLevel(logging.DEBUG)

class TestCaseManager:
    """基於 SQLite 的測試案例管理器"""
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化測試案例管理器
        
        Args:
            data_dir: 為了向後兼容保留此參數，但實際使用 SQLite
        """
        # 向後兼容，但實際上使用 SQLite
        pass
    
    # ========== Product Tags 管理 ==========
    
    def get_product_tags(self) -> List[Dict]:
        """取得所有產品標籤"""
        query = """
            SELECT id, name, description, color, created_at, updated_at
            FROM product_tags 
            ORDER BY name
        """
        return db_manager.execute_query(query)
    
    def create_product_tag(self, name: str, description: Optional[str] = None, 
                          color: str = '#007bff') -> Dict:
        """建立產品標籤"""
        query = """
            INSERT INTO product_tags (name, description, color)
            VALUES (?, ?, ?)
        """
        tag_id = db_manager.execute_insert(query, (name, description, color))
        
        # 返回新創建的標籤
        return self.get_product_tag_by_id(int(tag_id))
    
    def get_product_tag_by_id(self, tag_id: int) -> Optional[Dict]:
        """根據 ID 取得產品標籤"""
        query = """
            SELECT id, name, description, color, created_at, updated_at
            FROM product_tags 
            WHERE id = ?
        """
        results = db_manager.execute_query(query, (tag_id,))
        return results[0] if results else None
    
    def get_product_tag_by_name(self, name: str) -> Optional[Dict]:
        """根據名稱取得產品標籤"""
        query = """
            SELECT id, name, description, color, created_at, updated_at
            FROM product_tags 
            WHERE name = ?
        """
        results = db_manager.execute_query(query, (name,))
        return results[0] if results else None
    
    def update_product_tag(self, tag_id: int, name: str = None, 
                          description: str = None, color: str = None) -> bool:
        """更新產品標籤"""
        update_fields = []
        params = []
        
        if name is not None:
            update_fields.append("name = ?")
            params.append(name)
        
        if description is not None:
            update_fields.append("description = ?")
            params.append(description)
        
        if color is not None:
            update_fields.append("color = ?")
            params.append(color)
        
        if not update_fields:
            return False
        
        params.append(tag_id)
        query = f"UPDATE product_tags SET {', '.join(update_fields)} WHERE id = ?"
        
        rows_affected = db_manager.execute_update(query, tuple(params))
        return rows_affected > 0
    
    def delete_product_tag(self, tag_id: int) -> bool:
        """刪除產品標籤"""
        query = "DELETE FROM product_tags WHERE id = ?"
        rows_affected = db_manager.execute_delete(query, (tag_id,))
        return rows_affected > 0
    
    # ========== Test Projects 管理 ==========
    
    def get_test_projects(self) -> List[Dict]:
        """取得所有測試專案"""
        db_logger.info("🚀 開始取得所有測試專案")
        try:
            query = """
                SELECT 
                    tp.id, tp.name, tp.description, tp.status, tp.responsible_user_id,
                    tp.created_at, tp.updated_at, tp.start_time, tp.end_time,
                    u.username as responsible_user_name
                FROM test_projects tp
                LEFT JOIN users u ON tp.responsible_user_id = u.id
                ORDER BY tp.created_at DESC
            """
            db_logger.info(f"📊 執行查詢: {query}")
            projects = db_manager.execute_query(query)
            db_logger.info(f"📊 查詢結果: 取得 {len(projects) if projects else 0} 個專案")
            
            if not projects:
                db_logger.info("📭 沒有找到任何測試專案")
                return []
            
            # 為每個專案添加測試案例和測試結果
            for i, project in enumerate(projects):
                db_logger.info(f"🔄 處理專案 {i+1}/{len(projects)}: {project.get('name', 'Unknown')}")
                try:
                    # 添加專案關聯的測試案例 ID 列表
                    test_cases = self.get_test_cases(project_id=project['id'])
                    project['selected_test_cases'] = [tc['id'] for tc in test_cases]
                    db_logger.info(f"📋 專案 {project['id']} 有 {len(test_cases)} 個測試案例")
                    
                    # 添加測試結果
                    project['test_results'] = self.get_test_results_for_project(project['id'])
                    db_logger.info(f"📋 專案 {project['id']} 有 {len(project['test_results'])} 個測試結果")
                except Exception as e:
                    db_logger.error(f"💥 處理專案 {project['id']} 失敗: {str(e)}")
                    # 設置默認值以防止整個流程中斷
                    project['selected_test_cases'] = []
                    project['test_results'] = []
            
            db_logger.info(f"✅ 成功處理完所有 {len(projects)} 個專案")
            return projects
            
        except Exception as e:
            db_logger.error(f"💥 取得測試專案失敗: {str(e)}")
            db_logger.error(f"💥 錯誤類型: {type(e).__name__}")
            import traceback
            db_logger.error(f"💥 完整錯誤堆疊:\n{traceback.format_exc()}")
            raise e
    
    def create_test_project(self, name: str, description: Optional[str] = None,
                           responsible_user_id: Optional[str] = None,
                           start_time: Optional[str] = None,
                           end_time: Optional[str] = None) -> Dict:
        """建立測試專案"""
        query = """
            INSERT INTO test_projects (name, description, responsible_user_id, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
        """
        project_id = db_manager.execute_insert(query, (name, description, responsible_user_id, start_time, end_time))
        
        # 返回新創建的專案
        return self.get_test_project_by_id(int(project_id))
    
    def get_test_project_by_id(self, project_id: int) -> Optional[Dict]:
        """根據 ID 取得測試專案"""
        query = """
            SELECT 
                tp.id, tp.name, tp.description, tp.status, tp.responsible_user_id,
                tp.created_at, tp.updated_at, tp.start_time, tp.end_time,
                u.username as responsible_user_name
            FROM test_projects tp
            LEFT JOIN users u ON tp.responsible_user_id = u.id
            WHERE tp.id = ?
        """
        results = db_manager.execute_query(query, (project_id,))
        
        if results:
            project = results[0]
            
            # 添加專案關聯的測試案例 ID 列表
            test_cases = self.get_test_cases(project_id=project_id)
            project['selected_test_cases'] = [tc['id'] for tc in test_cases]
            
            # 添加實際的測試結果
            project['test_results'] = self.get_test_results_for_project(project_id)
            
            return project
        
        return None
    
    def get_test_project_by_name(self, name: str) -> Optional[Dict]:
        """根據名稱取得測試專案"""
        query = """
            SELECT 
                tp.id, tp.name, tp.description, tp.status, tp.responsible_user_id,
                tp.created_at, tp.updated_at, tp.start_time, tp.end_time,
                u.username as responsible_user_name
            FROM test_projects tp
            LEFT JOIN users u ON tp.responsible_user_id = u.id
            WHERE tp.name = ?
        """
        results = db_manager.execute_query(query, (name,))
        
        if results:
            project = results[0]
            
            # 添加專案關聯的測試案例 ID 列表
            test_cases = self.get_test_cases(project_id=project['id'])
            project['selected_test_cases'] = [tc['id'] for tc in test_cases]
            
            # 添加實際的測試結果
            project['test_results'] = self.get_test_results_for_project(project['id'])
            
            return project
        
        return None
    
    def update_test_project(self, project_id: int, name: str = None, 
                           description: str = None, status: str = None,
                           responsible_user_id: str = None,
                           start_time: str = None, end_time: str = None) -> bool:
        """更新測試專案"""
        update_fields = []
        params = []
        
        if name is not None:
            update_fields.append("name = ?")
            params.append(name)
        
        if description is not None:
            update_fields.append("description = ?")
            params.append(description)
        
        if status is not None:
            update_fields.append("status = ?")
            params.append(status)
        
        if responsible_user_id is not None:
            update_fields.append("responsible_user_id = ?")
            params.append(responsible_user_id)
        
        if start_time is not None:
            update_fields.append("start_time = ?")
            params.append(start_time)
        
        if end_time is not None:
            update_fields.append("end_time = ?")
            params.append(end_time)
        
        if not update_fields:
            return False
        
        params.append(project_id)
        query = f"UPDATE test_projects SET {', '.join(update_fields)} WHERE id = ?"
        
        rows_affected = db_manager.execute_update(query, tuple(params))
        return rows_affected > 0
    
    def delete_test_project(self, project_id: int) -> bool:
        """刪除測試專案"""
        query = "DELETE FROM test_projects WHERE id = ?"
        rows_affected = db_manager.execute_delete(query, (project_id,))
        return rows_affected > 0
    
    def clear_project_test_cases(self, project_id: int) -> bool:
        """清除專案的所有測試案例關聯"""
        query = "UPDATE test_cases SET test_project_id = NULL WHERE test_project_id = ?"
        rows_affected = db_manager.execute_update(query, (project_id,))
        return True  # 即使沒有關聯的案例也返回成功
    
    # ========== Test Cases 管理 ==========
    
    def get_test_cases(self, project_id: Optional[int] = None, 
                      status: Optional[str] = None) -> List[Dict]:
        """取得測試案例"""
        query = """
            SELECT 
                tc.id, tc.tc_id, tc.title, tc.description, tc.acceptance_criteria,
                tc.priority, tc.status, tc.test_project_id, tc.responsible_user_id,
                tc.estimated_hours, tc.actual_hours, tc.created_at, tc.updated_at,
                tp.name as project_name,
                u.username as responsible_user_name
            FROM test_cases tc
            LEFT JOIN test_projects tp ON tc.test_project_id = tp.id
            LEFT JOIN users u ON tc.responsible_user_id = u.id
        """
        
        conditions = []
        params = []
        
        if project_id is not None:
            conditions.append("tc.test_project_id = ?")
            params.append(project_id)
        
        if status is not None:
            conditions.append("tc.status = ?")
            params.append(status)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY tc.tc_id"
        
        test_cases = db_manager.execute_query(query, tuple(params))
        
        # 為每個測試案例添加標籤信息
        for tc in test_cases:
            tc['product_tags'] = self.get_test_case_tags(tc['id'])
        
        return test_cases
    
    def create_test_case(self, title: str, description: Optional[str] = None,
                        acceptance_criteria: Optional[str] = None,
                        priority: str = 'medium', status: str = 'draft',
                        test_project_id: Optional[int] = None,
                        responsible_user_id: Optional[str] = None,
                        estimated_hours: float = 0,
                        product_tag_ids: Optional[List[int]] = None) -> Dict:
        """建立測試案例"""
        # 生成 TC ID
        tc_id = self._generate_tc_id()
        
        query = """
            INSERT INTO test_cases (
                tc_id, title, description, acceptance_criteria, priority, status,
                test_project_id, responsible_user_id, estimated_hours
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        test_case_id = db_manager.execute_insert(query, (
            tc_id, title, description, acceptance_criteria, priority, status,
            test_project_id, responsible_user_id, estimated_hours
        ))
        
        # 添加產品標籤關聯
        if product_tag_ids:
            self._add_test_case_tags(int(test_case_id), product_tag_ids)
        
        # 返回新創建的測試案例
        return self.get_test_case_by_id(int(test_case_id))
    
    def get_test_case_by_id(self, test_case_id: int) -> Optional[Dict]:
        """根據 ID 取得測試案例"""
        query = """
            SELECT 
                tc.id, tc.tc_id, tc.title, tc.description, tc.acceptance_criteria,
                tc.priority, tc.status, tc.test_project_id, tc.responsible_user_id,
                tc.estimated_hours, tc.actual_hours, tc.created_at, tc.updated_at,
                tp.name as project_name,
                u.username as responsible_user_name
            FROM test_cases tc
            LEFT JOIN test_projects tp ON tc.test_project_id = tp.id
            LEFT JOIN users u ON tc.responsible_user_id = u.id
            WHERE tc.id = ?
        """
        results = db_manager.execute_query(query, (test_case_id,))
        
        if results:
            tc = results[0]
            tc['product_tags'] = self.get_test_case_tags(tc['id'])
            return tc
        
        return None
    
    def get_test_case_by_tc_id(self, tc_id: str) -> Optional[Dict]:
        """根據 TC ID 取得測試案例"""
        query = """
            SELECT 
                tc.id, tc.tc_id, tc.title, tc.description, tc.acceptance_criteria,
                tc.priority, tc.status, tc.test_project_id, tc.responsible_user_id,
                tc.estimated_hours, tc.actual_hours, tc.created_at, tc.updated_at,
                tp.name as project_name,
                u.username as responsible_user_name
            FROM test_cases tc
            LEFT JOIN test_projects tp ON tc.test_project_id = tp.id
            LEFT JOIN users u ON tc.responsible_user_id = u.id
            WHERE tc.tc_id = ?
        """
        results = db_manager.execute_query(query, (tc_id,))
        
        if results:
            tc = results[0]
            tc['product_tags'] = self.get_test_case_tags(tc['id'])
            return tc
        
        return None
    
    def update_test_case(self, test_case_id: int, **kwargs) -> bool:
        """更新測試案例"""
        allowed_fields = [
            'title', 'description', 'acceptance_criteria', 'priority', 'status',
            'test_project_id', 'responsible_user_id', 'estimated_hours', 'actual_hours'
        ]
        
        # 處理產品標籤更新
        product_tag_ids = kwargs.pop('product_tag_ids', None)
        
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        # 更新基本欄位
        if update_fields:
            params.append(test_case_id)
            query = f"UPDATE test_cases SET {', '.join(update_fields)} WHERE id = ?"
            db_manager.execute_update(query, tuple(params))
        
        # 更新產品標籤
        if product_tag_ids is not None:
            self.update_test_case_tags(test_case_id, product_tag_ids)
        
        return True
    
    def delete_test_case(self, test_case_id: int) -> bool:
        """刪除測試案例"""
        query = "DELETE FROM test_cases WHERE id = ?"
        rows_affected = db_manager.execute_delete(query, (test_case_id,))
        return rows_affected > 0
    
    def get_test_case_tags(self, test_case_id: int) -> List[Dict]:
        """取得測試案例的標籤"""
        query = """
            SELECT pt.id, pt.name, pt.description, pt.color
            FROM product_tags pt
            INNER JOIN test_case_tags tct ON pt.id = tct.product_tag_id
            WHERE tct.test_case_id = ?
            ORDER BY pt.name
        """
        return db_manager.execute_query(query, (test_case_id,))
    
    def _add_test_case_tags(self, test_case_id: int, tag_ids: List[int]):
        """添加測試案例標籤關聯"""
        query = "INSERT INTO test_case_tags (test_case_id, product_tag_id) VALUES (?, ?)"
        params_list = [(test_case_id, tag_id) for tag_id in tag_ids]
        db_manager.execute_many(query, params_list)
    
    def _remove_test_case_tags(self, test_case_id: int, tag_ids: List[int] = None):
        """移除測試案例標籤關聯"""
        if tag_ids:
            placeholders = ','.join(['?'] * len(tag_ids))
            query = f"DELETE FROM test_case_tags WHERE test_case_id = ? AND product_tag_id IN ({placeholders})"
            params = [test_case_id] + tag_ids
        else:
            query = "DELETE FROM test_case_tags WHERE test_case_id = ?"
            params = [test_case_id]
        
        db_manager.execute_delete(query, tuple(params))
    
    def update_test_case_tags(self, test_case_id: int, tag_ids: List[int]):
        """更新測試案例標籤"""
        # 先移除所有現有標籤
        self._remove_test_case_tags(test_case_id)
        
        # 添加新標籤
        if tag_ids:
            self._add_test_case_tags(test_case_id, tag_ids)
    
    def _generate_tc_id(self) -> str:
        """生成 TC ID"""
        # 獲取最大的 TC ID 序號，而不是使用 COUNT
        query = """
            SELECT tc_id FROM test_cases 
            WHERE tc_id LIKE 'TC%' 
            ORDER BY CAST(SUBSTR(tc_id, 3) AS INTEGER) DESC 
            LIMIT 1
        """
        result = db_manager.execute_query(query)
        
        if result and result[0]['tc_id']:
            # 從最後一個 TC ID 提取序號並加 1
            last_tc_id = result[0]['tc_id']
            last_number = int(last_tc_id[2:])  # 移除 'TC' 前綴
            next_number = last_number + 1
        else:
            # 如果沒有現有的 TC ID，從 1 開始
            next_number = 1
            
        return f"TC{next_number:05d}"  # TC00001, TC00002, ...
    
    # ========== 統計相關 ==========
    
    def get_test_case_statistics(self) -> Dict:
        """取得測試案例統計"""
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) as draft,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'blocked' THEN 1 ELSE 0 END) as blocked,
                SUM(estimated_hours) as total_estimated_hours,
                SUM(actual_hours) as total_actual_hours
            FROM test_cases
        """
        results = db_manager.execute_query(query)
        return results[0] if results else {}
    
    def get_project_statistics(self, project_id: int) -> Dict:
        """取得專案統計"""
        query = """
            SELECT 
                COUNT(*) as total_cases,
                SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) as draft,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'blocked' THEN 1 ELSE 0 END) as blocked,
                SUM(estimated_hours) as total_estimated_hours,
                SUM(actual_hours) as total_actual_hours
            FROM test_cases
            WHERE test_project_id = ?
        """
        results = db_manager.execute_query(query, (project_id,))
        return results[0] if results else {}
    
    def update_test_result(self, project_id: str, test_case_id: str, status, 
                          notes: str = None, known_issues: str = None, 
                          blocked_reason: str = None) -> Optional[Dict]:
        """更新測試結果"""
        try:
            # 轉換 project_id 為整數
            project_id = int(project_id)
            test_case_id = int(test_case_id)
            
            # 轉換狀態枚舉為字符串
            status_str = status.value if hasattr(status, 'value') else str(status)
            
            # 檢查專案是否存在
            project = self.get_test_project_by_id(project_id)
            if not project:
                return None
            
            # 檢查測試案例是否存在
            test_case = self.get_test_case_by_id(test_case_id)
            if not test_case:
                return None
            
            # 使用 UPSERT 語法更新或插入測試結果
            upsert_query = """
                INSERT INTO test_results (project_id, test_case_id, status, notes, known_issues, blocked_reason, tested_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(project_id, test_case_id) 
                DO UPDATE SET 
                    status = excluded.status,
                    notes = excluded.notes,
                    known_issues = excluded.known_issues,
                    blocked_reason = excluded.blocked_reason,
                    tested_at = excluded.tested_at,
                    updated_at = excluded.updated_at
            """
            
            db_manager.execute_update(upsert_query, (
                project_id, test_case_id, status_str, 
                notes or '', known_issues or '', blocked_reason or ''
            ))
            
            # 重新獲取專案以包含更新的測試結果
            return self.get_test_project_by_id(project_id)
            
        except Exception as e:
            print(f"更新測試結果失敗: {e}")
            return None
    
    def get_test_results_for_project(self, project_id: int) -> Dict[str, Dict]:
        """取得專案的所有測試結果"""
        query = """
            SELECT test_case_id, status, notes, known_issues, blocked_reason, tested_at
            FROM test_results 
            WHERE project_id = ?
        """
        results = db_manager.execute_query(query, (project_id,))
        
        test_results = {}
        for result in results:
            test_results[str(result['test_case_id'])] = {
                'test_case_id': result['test_case_id'],
                'status': result['status'],
                'notes': result['notes'] or '',
                'known_issues': result['known_issues'] or '',
                'blocked_reason': result['blocked_reason'] or '',
                'tested_at': result['tested_at']
            }
        
        return test_results
    
    # ========== 向後兼容方法 ==========
    
    def get_all_projects(self) -> Dict[str, Dict]:
        """取得所有專案（向後兼容格式）"""
        projects = self.get_test_projects()
        return {project['name']: project for project in projects}
    
    def get_project_test_cases_count(self, project_name: str) -> int:
        """取得專案的測試案例數量"""
        project = self.get_test_project_by_name(project_name)
        if project:
            stats = self.get_project_statistics(project['id'])
            return stats.get('total_cases', 0)
        return 0
    
    def delete_project(self, project_name: str) -> bool:
        """根據名稱刪除專案"""
        project = self.get_test_project_by_name(project_name)
        if project:
            return self.delete_test_project(project['id'])
        return False