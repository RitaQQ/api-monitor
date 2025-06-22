import sqlite3
import os
import threading
from contextlib import contextmanager
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import sys

# 配置詳細的日誌輸出
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# 創建專門的 logger
sql_logger = logging.getLogger('database')
sql_logger.setLevel(logging.DEBUG)

class DatabaseManager:
    """SQLite 資料庫管理器"""
    
    def __init__(self, db_path: str = "data/api_monitor.db"):
        self.db_path = db_path
        self.connection_pool = threading.local()
        self._ensure_database_exists()
        self._initialize_database()
    
    def _ensure_database_exists(self):
        """確保資料庫目錄存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """獲取資料庫連接（線程安全）"""
        if not hasattr(self.connection_pool, 'connection'):
            self.connection_pool.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            # 啟用外鍵約束
            self.connection_pool.connection.execute("PRAGMA foreign_keys = ON")
            # 設置 Row factory 以便獲取字典格式結果
            self.connection_pool.connection.row_factory = sqlite3.Row
        
        return self.connection_pool.connection
    
    @contextmanager
    def get_db_cursor(self, commit: bool = True):
        """獲取資料庫游標的上下文管理器"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def _initialize_database(self):
        """初始化資料庫結構"""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            with self.get_db_cursor() as cursor:
                cursor.executescript(schema_sql)
        
        # 創建預設管理員用戶（如果不存在）
        self._create_default_admin()
    
    def _create_default_admin(self):
        """創建預設管理員用戶"""
        import uuid
        import hashlib
        
        admin_id = str(uuid.uuid4())
        username = 'admin'
        password = 'admin123'
        # 使用與 UserManager 相同的加密方式
        salt = "api_monitor_salt_2025"
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        with self.get_db_cursor() as cursor:
            # 檢查是否已存在管理員
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO users (id, username, password_hash, role, email)
                    VALUES (?, ?, ?, ?, ?)
                """, (admin_id, username, password_hash, 'admin', 'admin@example.com'))
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """執行查詢並返回結果"""
        sql_logger.info(f"🔍 執行 SQL 查詢")
        sql_logger.info(f"📝 SQL: {query}")
        sql_logger.info(f"📊 參數: {params}")
        
        try:
            with self.get_db_cursor(commit=False) as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                result = [dict(row) for row in rows]
                sql_logger.info(f"✅ 查詢成功，返回 {len(result)} 筆記錄")
                return result
        except Exception as e:
            sql_logger.error(f"💥 SQL 查詢失敗: {str(e)}")
            sql_logger.error(f"💥 錯誤類型: {type(e).__name__}")
            sql_logger.error(f"💥 SQL: {query}")
            sql_logger.error(f"💥 參數: {params}")
            import traceback
            sql_logger.error(f"💥 完整錯誤堆疊:\n{traceback.format_exc()}")
            raise e
    
    def execute_insert(self, query: str, params: tuple = ()) -> str:
        """執行插入並返回 lastrowid"""
        with self.get_db_cursor() as cursor:
            cursor.execute(query, params)
            return str(cursor.lastrowid)
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """執行更新並返回影響的行數"""
        with self.get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def execute_delete(self, query: str, params: tuple = ()) -> int:
        """執行刪除並返回影響的行數"""
        with self.get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """批量執行 SQL 語句"""
        with self.get_db_cursor() as cursor:
            cursor.executemany(query, params_list)
    
    def table_exists(self, table_name: str) -> bool:
        """檢查表是否存在"""
        with self.get_db_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table_name,))
            return cursor.fetchone() is not None
    
    def get_table_info(self, table_name: str) -> List[Dict]:
        """獲取表結構信息"""
        with self.get_db_cursor(commit=False) as cursor:
            cursor.execute(f"PRAGMA table_info({table_name})")
            return [dict(row) for row in cursor.fetchall()]
    
    def backup_database(self, backup_path: str):
        """備份資料庫"""
        import shutil
        shutil.copy2(self.db_path, backup_path)
    
    def close_all_connections(self):
        """關閉所有連接"""
        if hasattr(self.connection_pool, 'connection'):
            self.connection_pool.connection.close()
            del self.connection_pool.connection

# 全域資料庫管理器實例
db_manager = DatabaseManager()