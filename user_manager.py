import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from database.db_manager import db_manager

class UserManager:
    """基於 SQLite 的用戶管理器"""
    
    def __init__(self, users_file: str = None):
        """
        初始化用戶管理器
        
        Args:
            users_file: 為了向後兼容保留此參數，但實際使用 SQLite
        """
        # 向後兼容，但實際上使用 SQLite
        pass
    
    def hash_password(self, password: str) -> str:
        """加密密碼"""
        # 使用 SHA-256 加密，在實際產品中應使用更安全的方法如 bcrypt
        salt = "api_monitor_salt_2025"  # 在實際應用中應使用隨機salt
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def load_users(self) -> List[Dict]:
        """載入所有用戶"""
        query = """
            SELECT id, username, password_hash, email, role, created_at, updated_at
            FROM users 
            ORDER BY created_at DESC
        """
        return db_manager.execute_query(query)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """驗證用戶登入"""
        password_hash = self.hash_password(password)
        query = """
            SELECT id, username, password_hash, email, role, created_at, updated_at
            FROM users 
            WHERE username = ? AND password_hash = ?
        """
        results = db_manager.execute_query(query, (username, password_hash))
        
        if results:
            user = results[0]
            # 更新最後登入時間（可以添加 last_login 欄位到資料庫）
            return user
        
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """根據 ID 獲取用戶"""
        query = """
            SELECT id, username, password_hash, email, role, created_at, updated_at
            FROM users 
            WHERE id = ?
        """
        results = db_manager.execute_query(query, (user_id,))
        return results[0] if results else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """根據用戶名獲取用戶"""
        query = """
            SELECT id, username, password_hash, email, role, created_at, updated_at
            FROM users 
            WHERE username = ?
        """
        results = db_manager.execute_query(query, (username,))
        return results[0] if results else None
    
    def create_user_legacy(self, username: str, password: str, role: str = 'user', 
                   email: str = None) -> Tuple[bool, str]:
        """創建新用戶（傳統格式）"""
        # 檢查用戶名是否已存在
        if self.get_user_by_username(username):
            return False, f"用戶名 '{username}' 已經存在"
        
        # 驗證角色
        if role not in ['admin', 'user']:
            return False, "角色必須是 'admin' 或 'user'"
        
        # 驗證密碼長度
        if len(password) < 6:
            return False, "密碼長度至少需要 6 個字符"
        
        try:
            user_id = str(uuid.uuid4())
            password_hash = self.hash_password(password)
            
            query = """
                INSERT INTO users (id, username, password_hash, email, role)
                VALUES (?, ?, ?, ?, ?)
            """
            
            db_manager.execute_insert(query, (user_id, username, password_hash, email, role))
            
            return True, f"用戶 '{username}' 創建成功"
            
        except Exception as e:
            return False, f"創建用戶時發生錯誤: {str(e)}"
    
    def update_user_legacy(self, user_id: str, username: str = None, email: str = None, 
                   role: str = None, password: str = None) -> Tuple[bool, str]:
        """更新用戶信息（傳統格式）"""
        # 檢查用戶是否存在
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "用戶不存在"
        
        # 如果要更新用戶名，檢查是否與其他用戶重複
        if username and username != user['username']:
            existing_user = self.get_user_by_username(username)
            if existing_user and existing_user['id'] != user_id:
                return False, f"用戶名 '{username}' 已經存在"
        
        try:
            # 構建更新查詢
            update_fields = []
            params = []
            
            if username:
                update_fields.append("username = ?")
                params.append(username)
            
            if email is not None:  # 允許設置為空字符串
                update_fields.append("email = ?")
                params.append(email)
            
            if role and role in ['admin', 'user']:
                update_fields.append("role = ?")
                params.append(role)
            
            if password:
                if len(password) < 6:
                    return False, "密碼長度至少需要 6 個字符"
                update_fields.append("password_hash = ?")
                params.append(self.hash_password(password))
            
            if not update_fields:
                return False, "沒有要更新的欄位"
            
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            
            rows_affected = db_manager.execute_update(query, tuple(params))
            
            if rows_affected > 0:
                return True, "用戶信息更新成功"
            else:
                return False, "更新失敗"
                
        except Exception as e:
            return False, f"更新用戶時發生錯誤: {str(e)}"
    
    def delete_user_legacy(self, user_id: str, current_user_id: str) -> Tuple[bool, str]:
        """刪除用戶（傳統格式）"""
        # 不能刪除自己
        if user_id == current_user_id:
            return False, "不能刪除自己的帳號"
        
        # 檢查用戶是否存在
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "用戶不存在"
        
        try:
            query = "DELETE FROM users WHERE id = ?"
            rows_affected = db_manager.execute_delete(query, (user_id,))
            
            if rows_affected > 0:
                return True, f"用戶 '{user['username']}' 已成功刪除"
            else:
                return False, "刪除失敗"
                
        except Exception as e:
            return False, f"刪除用戶時發生錯誤: {str(e)}"
    
    def get_all_users(self) -> List[Dict]:
        """獲取所有用戶（不包含密碼）"""
        query = """
            SELECT id, username, email, role, created_at, updated_at
            FROM users 
            ORDER BY created_at DESC
        """
        return db_manager.execute_query(query)
    
    def get_user_stats(self) -> Dict:
        """獲取用戶統計信息"""
        query = """
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admin_count,
                SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as user_count
            FROM users
        """
        results = db_manager.execute_query(query)
        
        if results:
            stats = results[0]
            return {
                'total_users': stats['total_users'],
                'admin_count': stats['admin_count'],
                'user_count': stats['user_count']
            }
        
        return {'total_users': 0, 'admin_count': 0, 'user_count': 0}
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """更改密碼"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "用戶不存在"
        
        # 驗證舊密碼
        old_password_hash = self.hash_password(old_password)
        if user['password_hash'] != old_password_hash:
            return False, "舊密碼不正確"
        
        # 驗證新密碼
        if len(new_password) < 6:
            return False, "新密碼長度至少需要 6 個字符"
        
        if old_password == new_password:
            return False, "新密碼不能與舊密碼相同"
        
        try:
            new_password_hash = self.hash_password(new_password)
            query = "UPDATE users SET password_hash = ? WHERE id = ?"
            
            rows_affected = db_manager.execute_update(query, (new_password_hash, user_id))
            
            if rows_affected > 0:
                return True, "密碼修改成功"
            else:
                return False, "密碼修改失敗"
                
        except Exception as e:
            return False, f"修改密碼時發生錯誤: {str(e)}"
    
    def is_admin(self, user_id: str) -> bool:
        """檢查用戶是否為管理員"""
        user = self.get_user_by_id(user_id)
        return user and user.get('role') == 'admin'
    
    def get_users_by_role(self, role: str) -> List[Dict]:
        """根據角色獲取用戶列表"""
        query = """
            SELECT id, username, email, role, created_at, updated_at
            FROM users 
            WHERE role = ?
            ORDER BY created_at DESC
        """
        return db_manager.execute_query(query, (role,))
    
    # ========== 測試期望的方法格式 ==========
    
    def create_user(self, username: str, password: str, email: str, role: str) -> Dict:
        """創建新用戶（測試期望的格式）"""
        # 驗證輸入
        if not username or not username.strip():
            raise ValueError("用戶名不能為空")
        
        if not password or not password.strip():
            raise ValueError("密碼不能為空")
        
        if role not in ['admin', 'user']:
            raise ValueError("角色必須是 'admin' 或 'user'")
        
        # 檢查用戶名是否已存在
        if self.get_user_by_username(username):
            raise Exception(f"用戶名 '{username}' 已經存在")
        
        try:
            user_id = str(uuid.uuid4())
            password_hash = self.hash_password(password)
            
            query = """
                INSERT INTO users (id, username, password_hash, email, role)
                VALUES (?, ?, ?, ?, ?)
            """
            
            db_manager.execute_insert(query, (user_id, username, password_hash, email, role))
            
            # 返回創建的用戶信息
            return {
                'id': user_id,
                'username': username,
                'email': email,
                'role': role,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"創建用戶時發生錯誤: {str(e)}")
    
    def update_user(self, user_id: str, **kwargs) -> Optional[Dict]:
        """更新用戶信息（測試期望的格式）"""
        # 檢查用戶是否存在
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        try:
            # 構建更新查詢
            update_fields = []
            params = []
            
            for field, value in kwargs.items():
                if field == 'username' and value:
                    # 檢查用戶名是否重複
                    existing_user = self.get_user_by_username(value)
                    if existing_user and existing_user['id'] != user_id:
                        raise Exception(f"用戶名 '{value}' 已經存在")
                    update_fields.append("username = ?")
                    params.append(value)
                elif field == 'email':
                    update_fields.append("email = ?")
                    params.append(value)
                elif field == 'role' and value in ['admin', 'user']:
                    update_fields.append("role = ?")
                    params.append(value)
            
            if update_fields:
                params.append(user_id)
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
                db_manager.execute_update(query, tuple(params))
            
            # 返回更新後的用戶信息
            return self.get_user_by_id(user_id)
                
        except Exception as e:
            raise Exception(f"更新用戶時發生錯誤: {str(e)}")
    
    def update_user_password(self, user_id: str, new_password: str) -> Optional[Dict]:
        """更新用戶密碼（測試期望的格式）"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        try:
            new_password_hash = self.hash_password(new_password)
            query = "UPDATE users SET password_hash = ? WHERE id = ?"
            
            rows_affected = db_manager.execute_update(query, (new_password_hash, user_id))
            
            if rows_affected > 0:
                return self.get_user_by_id(user_id)
            else:
                return None
                
        except Exception as e:
            raise Exception(f"更新密碼時發生錯誤: {str(e)}")
    
    def delete_user(self, user_id: str) -> bool:
        """刪除用戶（測試期望的格式）"""
        # 檢查用戶是否存在
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        try:
            query = "DELETE FROM users WHERE id = ?"
            rows_affected = db_manager.execute_delete(query, (user_id,))
            return rows_affected > 0
                
        except Exception as e:
            return False
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """驗證密碼"""
        return self.hash_password(password) == hashed_password
    
    def get_user_statistics(self) -> Dict:
        """獲取用戶統計信息（測試期望的格式）"""
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admin_count,
                SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as user_count
            FROM users
        """
        results = db_manager.execute_query(query)
        
        if results:
            stats = results[0]
            return {
                'total': stats['total'] or 0,
                'by_role': {
                    'admin': stats['admin_count'] or 0,
                    'user': stats['user_count'] or 0
                }
            }
        
        return {
            'total': 0,
            'by_role': {'admin': 0, 'user': 0}
        }