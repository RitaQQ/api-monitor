import json
import hashlib
import os
from datetime import datetime
import uuid

class UserManager:
    def __init__(self, users_file='data/users.json'):
        self.users_file = users_file
        self.ensure_data_directory()
        self.init_users_file()
    
    def ensure_data_directory(self):
        """確保 data 目錄存在"""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
    
    def init_users_file(self):
        """初始化用戶檔案，如果不存在則創建並添加預設管理員"""
        if not os.path.exists(self.users_file):
            # 創建預設管理員帳號
            default_admin = {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "password_hash": self.hash_password("admin123"),
                "role": "admin",
                "email": "admin@api-monitor.com",
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "is_active": True
            }
            
            users_data = {
                "users": [default_admin],
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2, ensure_ascii=False)
            
            print(f"🔧 創建預設管理員帳號:")
            print(f"   用戶名: admin")
            print(f"   密碼: admin123")
            print(f"   角色: 管理員")
    
    def hash_password(self, password):
        """加密密碼"""
        # 使用 SHA-256 加密，在實際產品中應使用更安全的方法如 bcrypt
        salt = "api_monitor_salt_2025"  # 在實際應用中應使用隨機salt
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def load_users(self):
        """載入所有用戶"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('users', [])
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"錯誤：無法解析用戶檔案 {self.users_file}")
            return []
    
    def save_users(self, users):
        """保存用戶列表"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"created_at": datetime.now().isoformat(), "version": "1.0"}
        
        data['users'] = users
        data['updated_at'] = datetime.now().isoformat()
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def authenticate_user(self, username, password):
        """驗證用戶登入"""
        users = self.load_users()
        password_hash = self.hash_password(password)
        
        for user in users:
            if (user.get('username') == username and 
                user.get('password_hash') == password_hash and 
                user.get('is_active', True)):
                
                # 更新最後登入時間
                user['last_login'] = datetime.now().isoformat()
                self.save_users(users)
                
                # 返回用戶資訊（不包含密碼）
                safe_user = {k: v for k, v in user.items() if k != 'password_hash'}
                return safe_user
        
        return None
    
    def get_user_by_username(self, username):
        """根據用戶名獲取用戶"""
        users = self.load_users()
        for user in users:
            if user.get('username') == username:
                return {k: v for k, v in user.items() if k != 'password_hash'}
        return None
    
    def get_user_by_id(self, user_id):
        """根據ID獲取用戶"""
        users = self.load_users()
        for user in users:
            if user.get('id') == user_id:
                return {k: v for k, v in user.items() if k != 'password_hash'}
        return None
    
    def create_user(self, username, password, role='user', email=''):
        """創建新用戶"""
        users = self.load_users()
        
        # 檢查用戶名是否已存在
        if any(user.get('username') == username for user in users):
            return False, "用戶名已存在"
        
        # 驗證角色
        if role not in ['admin', 'user']:
            return False, "無效的用戶角色"
        
        # 創建新用戶
        new_user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "password_hash": self.hash_password(password),
            "role": role,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_active": True
        }
        
        users.append(new_user)
        self.save_users(users)
        
        return True, "用戶創建成功"
    
    def update_user(self, user_id, **kwargs):
        """更新用戶資訊"""
        users = self.load_users()
        
        for i, user in enumerate(users):
            if user.get('id') == user_id:
                # 允許更新的欄位
                allowed_fields = ['email', 'role', 'is_active']
                for field in allowed_fields:
                    if field in kwargs:
                        user[field] = kwargs[field]
                
                # 如果有新密碼，更新密碼
                if 'password' in kwargs and kwargs['password']:
                    user['password_hash'] = self.hash_password(kwargs['password'])
                
                user['updated_at'] = datetime.now().isoformat()
                users[i] = user
                self.save_users(users)
                return True, "用戶更新成功"
        
        return False, "用戶不存在"
    
    def delete_user(self, user_id, current_user_id):
        """刪除用戶（不能刪除自己）"""
        if user_id == current_user_id:
            return False, "不能刪除自己的帳號"
        
        users = self.load_users()
        original_count = len(users)
        
        users = [user for user in users if user.get('id') != user_id]
        
        if len(users) < original_count:
            self.save_users(users)
            return True, "用戶刪除成功"
        
        return False, "用戶不存在"
    
    def get_all_users(self):
        """獲取所有用戶（不包含密碼）"""
        users = self.load_users()
        return [{k: v for k, v in user.items() if k != 'password_hash'} for user in users]
    
    def get_user_stats(self):
        """獲取用戶統計資訊"""
        users = self.load_users()
        return {
            'total_users': len(users),
            'active_users': len([u for u in users if u.get('is_active', True)]),
            'admin_users': len([u for u in users if u.get('role') == 'admin']),
            'regular_users': len([u for u in users if u.get('role') == 'user'])
        }