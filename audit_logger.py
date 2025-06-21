import json
import uuid
from datetime import datetime
from typing import Dict, Optional, Any
from database.db_manager import db_manager
from flask import request, session


class AuditLogger:
    """操作記錄記錄器 - 只記錄關鍵操作，不要過度設計"""
    
    # 操作類型
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_LOGIN = 'LOGIN'
    ACTION_LOGOUT = 'LOGOUT'
    ACTION_PASSWORD_CHANGE = 'PASSWORD_CHANGE'
    
    # 資源類型
    RESOURCE_USER = 'USER'
    RESOURCE_API = 'API'
    RESOURCE_TEST_CASE = 'TEST_CASE'
    RESOURCE_TEST_PROJECT = 'TEST_PROJECT'
    
    @staticmethod
    def log_action(
        user_id: str,
        username: str,
        action: str,
        resource_type: str,
        resource_id: str = None,
        resource_name: str = None,
        old_values: Dict = None,
        new_values: Dict = None
    ):
        """記錄操作 - 簡單直接"""
        try:
            # 獲取請求信息
            ip_address = request.remote_addr if request else 'Unknown'
            user_agent = request.headers.get('User-Agent', 'Unknown') if request else 'Unknown'
            
            # 清理敏感信息
            if old_values:
                old_values = AuditLogger._clean_sensitive_data(old_values)
            if new_values:
                new_values = AuditLogger._clean_sensitive_data(new_values)
            
            query = """
                INSERT INTO audit_logs (
                    user_id, username, action, resource_type, resource_id, resource_name,
                    old_values, new_values, ip_address, user_agent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            db_manager.execute_insert(query, (
                user_id,
                username,
                action,
                resource_type,
                resource_id,
                resource_name,
                json.dumps(old_values, ensure_ascii=False) if old_values else None,
                json.dumps(new_values, ensure_ascii=False) if new_values else None,
                ip_address,
                user_agent
            ))
            
        except Exception as e:
            # 記錄失敗不應該影響主要業務流程
            print(f"審計日誌記錄失敗: {e}")
    
    @staticmethod
    def _clean_sensitive_data(data: Dict) -> Dict:
        """清理敏感信息"""
        if not isinstance(data, dict):
            return data
        
        cleaned = data.copy()
        sensitive_fields = ['password', 'password_hash', 'token', 'secret']
        
        for field in sensitive_fields:
            if field in cleaned:
                cleaned[field] = '***'
        
        return cleaned
    
    @staticmethod
    def log_user_login(user_id: str, username: str):
        """記錄用戶登入"""
        AuditLogger.log_action(
            user_id=user_id,
            username=username,
            action=AuditLogger.ACTION_LOGIN,
            resource_type=AuditLogger.RESOURCE_USER,
            resource_id=user_id,
            resource_name=username
        )
    
    @staticmethod
    def log_user_logout(user_id: str, username: str):
        """記錄用戶登出"""
        AuditLogger.log_action(
            user_id=user_id,
            username=username,
            action=AuditLogger.ACTION_LOGOUT,
            resource_type=AuditLogger.RESOURCE_USER,
            resource_id=user_id,
            resource_name=username
        )
    
    @staticmethod
    def log_user_create(operator_id: str, operator_name: str, new_user_data: Dict):
        """記錄用戶創建"""
        AuditLogger.log_action(
            user_id=operator_id,
            username=operator_name,
            action=AuditLogger.ACTION_CREATE,
            resource_type=AuditLogger.RESOURCE_USER,
            resource_id=new_user_data.get('id'),
            resource_name=new_user_data.get('username'),
            new_values=new_user_data
        )
    
    @staticmethod
    def log_user_update(operator_id: str, operator_name: str, user_id: str, 
                       old_data: Dict, new_data: Dict):
        """記錄用戶更新"""
        AuditLogger.log_action(
            user_id=operator_id,
            username=operator_name,
            action=AuditLogger.ACTION_UPDATE,
            resource_type=AuditLogger.RESOURCE_USER,
            resource_id=user_id,
            resource_name=new_data.get('username', old_data.get('username')),
            old_values=old_data,
            new_values=new_data
        )
    
    @staticmethod
    def log_user_delete(operator_id: str, operator_name: str, deleted_user_data: Dict):
        """記錄用戶刪除"""
        AuditLogger.log_action(
            user_id=operator_id,
            username=operator_name,
            action=AuditLogger.ACTION_DELETE,
            resource_type=AuditLogger.RESOURCE_USER,
            resource_id=deleted_user_data.get('id'),
            resource_name=deleted_user_data.get('username'),
            old_values=deleted_user_data
        )
    
    @staticmethod
    def log_api_create(user_id: str, username: str, api_data: Dict):
        """記錄API創建"""
        AuditLogger.log_action(
            user_id=user_id,
            username=username,
            action=AuditLogger.ACTION_CREATE,
            resource_type=AuditLogger.RESOURCE_API,
            resource_id=api_data.get('id'),
            resource_name=api_data.get('name'),
            new_values=api_data
        )
    
    @staticmethod
    def log_api_update(user_id: str, username: str, api_id: str, 
                      old_data: Dict, new_data: Dict):
        """記錄API更新"""
        AuditLogger.log_action(
            user_id=user_id,
            username=username,
            action=AuditLogger.ACTION_UPDATE,
            resource_type=AuditLogger.RESOURCE_API,
            resource_id=api_id,
            resource_name=new_data.get('name', old_data.get('name')),
            old_values=old_data,
            new_values=new_data
        )
    
    @staticmethod
    def log_api_delete(user_id: str, username: str, api_data: Dict):
        """記錄API刪除"""
        AuditLogger.log_action(
            user_id=user_id,
            username=username,
            action=AuditLogger.ACTION_DELETE,
            resource_type=AuditLogger.RESOURCE_API,
            resource_id=api_data.get('id'),
            resource_name=api_data.get('name'),
            old_values=api_data
        )
    
    @staticmethod
    def get_audit_logs(limit: int = 100, offset: int = 0, 
                      user_id: str = None, action: str = None, 
                      resource_type: str = None, start_date: str = None, 
                      end_date: str = None):
        """獲取審計日誌"""
        where_conditions = []
        params = []
        
        if user_id:
            where_conditions.append("user_id = ?")
            params.append(user_id)
        
        if action:
            where_conditions.append("action = ?")
            params.append(action)
        
        if resource_type:
            where_conditions.append("resource_type = ?")
            params.append(resource_type)
        
        if start_date:
            where_conditions.append("created_at >= ?")
            params.append(start_date)
        
        if end_date:
            where_conditions.append("created_at <= ?")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = f"""
            SELECT 
                id, user_id, username, action, resource_type, resource_id, resource_name,
                old_values, new_values, ip_address, user_agent, created_at
            FROM audit_logs 
            {where_clause}
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """
        
        params.extend([limit, offset])
        
        logs = db_manager.execute_query(query, tuple(params))
        
        # 解析JSON字段
        for log in logs:
            if log['old_values']:
                try:
                    log['old_values'] = json.loads(log['old_values'])
                except:
                    pass
            if log['new_values']:
                try:
                    log['new_values'] = json.loads(log['new_values'])
                except:
                    pass
        
        return logs
    
    @staticmethod
    def log_test_case_create(user_id: str, username: str, test_case_data: Dict):
        """記錄測試案例創建"""
        AuditLogger.log_action(
            user_id=user_id,
            username=username,
            action=AuditLogger.ACTION_CREATE,
            resource_type=AuditLogger.RESOURCE_TEST_CASE,
            resource_id=str(test_case_data.get('id')),
            resource_name=test_case_data.get('title'),
            new_values=test_case_data
        )
    
    @staticmethod
    def log_test_case_update(user_id: str, username: str, test_case_id: str, 
                            old_data: Dict, new_data: Dict):
        """記錄測試案例更新"""
        AuditLogger.log_action(
            user_id=user_id,
            username=username,
            action=AuditLogger.ACTION_UPDATE,
            resource_type=AuditLogger.RESOURCE_TEST_CASE,
            resource_id=test_case_id,
            resource_name=new_data.get('title', old_data.get('title')),
            old_values=old_data,
            new_values=new_data
        )
    
    @staticmethod
    def log_test_case_delete(user_id: str, username: str, test_case_data: Dict):
        """記錄測試案例刪除"""
        AuditLogger.log_action(
            user_id=user_id,
            username=username,
            action=AuditLogger.ACTION_DELETE,
            resource_type=AuditLogger.RESOURCE_TEST_CASE,
            resource_id=str(test_case_data.get('id')),
            resource_name=test_case_data.get('title'),
            old_values=test_case_data
        )
    
    @staticmethod
    def log_test_project_create(user_id: str, username: str, project_data: Dict):
        """記錄測試專案創建"""
        AuditLogger.log_action(
            user_id=user_id,
            username=username,
            action=AuditLogger.ACTION_CREATE,
            resource_type=AuditLogger.RESOURCE_TEST_PROJECT,
            resource_id=str(project_data.get('id')),
            resource_name=project_data.get('name'),
            new_values=project_data
        )
    
    @staticmethod
    def log_test_project_update(user_id: str, username: str, project_id: str,
                               old_data: Dict, new_data: Dict):
        """記錄測試專案更新"""
        AuditLogger.log_action(
            user_id=user_id,
            username=username,
            action=AuditLogger.ACTION_UPDATE,
            resource_type=AuditLogger.RESOURCE_TEST_PROJECT,
            resource_id=project_id,
            resource_name=new_data.get('name', old_data.get('name')),
            old_values=old_data,
            new_values=new_data
        )
    
    @staticmethod
    def log_test_project_delete(user_id: str, username: str, project_data: Dict):
        """記錄測試專案刪除"""
        AuditLogger.log_action(
            user_id=user_id,
            username=username,
            action=AuditLogger.ACTION_DELETE,
            resource_type=AuditLogger.RESOURCE_TEST_PROJECT,
            resource_id=str(project_data.get('id')),
            resource_name=project_data.get('name'),
            old_values=project_data
        )
    
    @staticmethod
    def get_audit_stats():
        """獲取審計統計"""
        query = """
            SELECT 
                action,
                resource_type,
                COUNT(*) as count
            FROM audit_logs 
            GROUP BY action, resource_type
            ORDER BY count DESC
        """
        
        stats = db_manager.execute_query(query)
        
        # 總計
        total_query = "SELECT COUNT(*) as total FROM audit_logs"
        total_result = db_manager.execute_query(total_query)
        total = total_result[0]['total'] if total_result else 0
        
        return {
            'total': total,
            'by_action_and_resource': stats
        }