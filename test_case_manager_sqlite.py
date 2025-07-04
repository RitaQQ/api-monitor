import json
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from database.db_manager import db_manager

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
        query = """
            SELECT 
                tp.id, tp.name, tp.description, tp.status, tp.responsible_user_id,
                tp.created_at, tp.updated_at,
                u.username as responsible_user_name
            FROM test_projects tp
            LEFT JOIN users u ON tp.responsible_user_id = u.id
            ORDER BY tp.created_at DESC
        """
        return db_manager.execute_query(query)
    
    def create_test_project(self, name: str, description: Optional[str] = None,
                           responsible_user_id: Optional[str] = None) -> Dict:
        """建立測試專案"""
        query = """
            INSERT INTO test_projects (name, description, responsible_user_id)
            VALUES (?, ?, ?)
        """
        project_id = db_manager.execute_insert(query, (name, description, responsible_user_id))
        
        # 返回新創建的專案
        return self.get_test_project_by_id(int(project_id))
    
    def get_test_project_by_id(self, project_id: int) -> Optional[Dict]:
        """根據 ID 取得測試專案"""
        query = """
            SELECT 
                tp.id, tp.name, tp.description, tp.status, tp.responsible_user_id,
                tp.created_at, tp.updated_at,
                u.username as responsible_user_name
            FROM test_projects tp
            LEFT JOIN users u ON tp.responsible_user_id = u.id
            WHERE tp.id = ?
        """
        results = db_manager.execute_query(query, (project_id,))
        return results[0] if results else None
    
    def get_test_project_by_name(self, name: str) -> Optional[Dict]:
        """根據名稱取得測試專案"""
        query = """
            SELECT 
                tp.id, tp.name, tp.description, tp.status, tp.responsible_user_id,
                tp.created_at, tp.updated_at,
                u.username as responsible_user_name
            FROM test_projects tp
            LEFT JOIN users u ON tp.responsible_user_id = u.id
            WHERE tp.name = ?
        """
        results = db_manager.execute_query(query, (name,))
        return results[0] if results else None
    
    def update_test_project(self, project_id: int, name: str = None, 
                           description: str = None, status: str = None,
                           responsible_user_id: str = None) -> bool:
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
        
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            return False
        
        params.append(test_case_id)
        query = f"UPDATE test_cases SET {', '.join(update_fields)} WHERE id = ?"
        
        rows_affected = db_manager.execute_update(query, tuple(params))
        return rows_affected > 0
    
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
        query = "SELECT COUNT(*) as count FROM test_cases"
        result = db_manager.execute_query(query)
        count = result[0]['count'] if result else 0
        return f"TC{count + 1:05d}"  # TC00001, TC00002, ...
    
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