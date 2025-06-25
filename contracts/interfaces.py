"""
QA Management Tool 接口契約定義
定義各模組間的標準接口，確保修改時的一致性
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

class TestStatus(Enum):
    """測試狀態枚舉"""
    DRAFT = "draft"
    READY = "ready" 
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class Priority(Enum):
    """優先級枚舉"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class UserRole(Enum):
    """用戶角色枚舉"""
    ADMIN = "admin"
    USER = "user"

# ========== 用戶管理器接口契約 ==========

class IUserManager(ABC):
    """用戶管理器接口契約"""
    
    @abstractmethod
    def create_user(self, username: str, password: str, email: str, role: str) -> Dict:
        """
        創建新用戶
        
        Args:
            username: 用戶名（必須唯一）
            password: 密碼（明文，內部會加密）
            email: 電子郵件
            role: 用戶角色（admin或user）
            
        Returns:
            Dict: 創建的用戶信息，包含id, username, email, role, created_at
            
        Raises:
            ValueError: 參數無效時
            Exception: 用戶名已存在或其他錯誤
        """
        pass
    
    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        根據ID獲取用戶
        
        Args:
            user_id: 用戶ID
            
        Returns:
            Optional[Dict]: 用戶信息或None
        """
        pass
    
    @abstractmethod
    def update_user(self, user_id: str, **kwargs) -> Optional[Dict]:
        """
        更新用戶信息
        
        Args:
            user_id: 用戶ID
            **kwargs: 要更新的欄位（username, email, role等）
            
        Returns:
            Optional[Dict]: 更新後的用戶信息或None
        """
        pass
    
    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """
        刪除用戶
        
        Args:
            user_id: 用戶ID
            
        Returns:
            bool: 是否成功刪除
        """
        pass
    
    @abstractmethod
    def get_user_statistics(self) -> Dict:
        """
        獲取用戶統計信息
        
        Returns:
            Dict: 統計信息，格式為:
            {
                'total': int,
                'by_role': {
                    'admin': int,
                    'user': int
                }
            }
        """
        pass

# ========== 測試案例管理器接口契約 ==========

class ITestCaseManager(ABC):
    """測試案例管理器接口契約"""
    
    @abstractmethod
    def create_test_case(self, title: str, description: Optional[str] = None,
                        acceptance_criteria: Optional[str] = None,
                        priority: str = 'medium', status: str = 'draft',
                        **kwargs) -> Dict:
        """
        創建測試案例
        
        Args:
            title: 測試案例標題（必需）
            description: 詳細描述
            acceptance_criteria: 驗收條件
            priority: 優先級（low/medium/high）
            status: 狀態（draft/ready/in_progress/completed/blocked）
            **kwargs: 其他可選參數
            
        Returns:
            Dict: 創建的測試案例信息
        """
        pass
    
    @abstractmethod
    def get_test_case_statistics(self) -> Dict:
        """
        獲取測試案例統計信息
        
        Returns:
            Dict: 統計信息，格式為:
            {
                'total': int,
                'by_status': {
                    'draft': int,
                    'ready': int,
                    'in_progress': int,
                    'completed': int,
                    'blocked': int
                },
                'by_priority': {
                    'low': int,
                    'medium': int,
                    'high': int
                }
            }
        """
        pass
    
    @abstractmethod
    def export_test_cases_to_csv(self) -> str:
        """
        導出測試案例為CSV格式
        
        Returns:
            str: CSV格式的測試案例數據
        """
        pass

# ========== API檢查器接口契約 ==========

class IAPIChecker(ABC):
    """API檢查器接口契約"""
    
    @abstractmethod
    def make_request(self, api_config: Dict) -> Tuple[str, float, str, str]:
        """
        發送HTTP請求並檢查API狀態
        
        Args:
            api_config: API配置，包含url, method, headers等
            
        Returns:
            Tuple[str, float, str, str]: (狀態, 響應時間, 錯誤消息, 響應內容)
            狀態為 'healthy' 或 'unhealthy'
        """
        pass
    
    @abstractmethod
    def validate_api_config(self, api_config: Dict) -> bool:
        """
        驗證API配置的有效性
        
        Args:
            api_config: API配置字典
            
        Returns:
            bool: 配置是否有效
        """
        pass

# ========== 壓力測試器接口契約 ==========

class IStressTester(ABC):
    """壓力測試器接口契約"""
    
    @abstractmethod
    def calculate_statistics(self, requests_data: List[Dict]) -> Dict:
        """
        計算壓力測試統計資料
        
        Args:
            requests_data: 請求結果數據列表
            
        Returns:
            Dict: 統計信息，包含成功率、響應時間等
        """
        pass
    
    @abstractmethod
    def validate_test_config(self, test_config: Dict) -> bool:
        """
        驗證壓力測試配置
        
        Args:
            test_config: 測試配置字典
            
        Returns:
            bool: 配置是否有效
        """
        pass

# ========== 資料庫管理器接口契約 ==========

class IDatabaseManager(ABC):
    """資料庫管理器接口契約"""
    
    @abstractmethod
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """
        執行SQL查詢
        
        Args:
            query: SQL查詢語句
            params: 查詢參數
            
        Returns:
            List[Dict]: 查詢結果列表
        """
        pass
    
    @abstractmethod
    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """
        執行插入操作
        
        Args:
            query: SQL插入語句
            params: 插入參數
            
        Returns:
            int: 新插入記錄的ID
        """
        pass
    
    @abstractmethod
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """
        執行更新操作
        
        Args:
            query: SQL更新語句
            params: 更新參數
            
        Returns:
            int: 受影響的行數
        """
        pass

# ========== 契約驗證器 ==========

class ContractValidator:
    """接口契約驗證器"""
    
    @staticmethod
    def validate_user_manager(instance) -> List[str]:
        """驗證用戶管理器是否符合接口契約"""
        errors = []
        
        # 檢查必要方法是否存在
        required_methods = [
            'create_user', 'get_user_by_id', 'update_user', 
            'delete_user', 'get_user_statistics'
        ]
        
        for method in required_methods:
            if not hasattr(instance, method):
                errors.append(f"缺少必要方法: {method}")
            elif not callable(getattr(instance, method)):
                errors.append(f"方法不可調用: {method}")
        
        return errors
    
    @staticmethod
    def validate_test_case_manager(instance) -> List[str]:
        """驗證測試案例管理器是否符合接口契約"""
        errors = []
        
        required_methods = [
            'create_test_case', 'get_test_case_statistics', 
            'export_test_cases_to_csv'
        ]
        
        for method in required_methods:
            if not hasattr(instance, method):
                errors.append(f"缺少必要方法: {method}")
            elif not callable(getattr(instance, method)):
                errors.append(f"方法不可調用: {method}")
        
        return errors
    
    @staticmethod
    def validate_all_contracts(user_manager, test_case_manager, api_checker=None, stress_tester=None) -> Dict[str, List[str]]:
        """驗證所有模組的接口契約"""
        results = {}
        
        results['user_manager'] = ContractValidator.validate_user_manager(user_manager)
        results['test_case_manager'] = ContractValidator.validate_test_case_manager(test_case_manager)
        
        if api_checker:
            results['api_checker'] = ContractValidator.validate_api_checker(api_checker)
        if stress_tester:
            results['stress_tester'] = ContractValidator.validate_stress_tester(stress_tester)
        
        return results
    
    @staticmethod
    def validate_api_checker(instance) -> List[str]:
        """驗證API檢查器是否符合接口契約"""
        errors = []
        
        required_methods = ['make_request', 'validate_api_config']
        
        for method in required_methods:
            if not hasattr(instance, method):
                errors.append(f"缺少必要方法: {method}")
            elif not callable(getattr(instance, method)):
                errors.append(f"方法不可調用: {method}")
        
        return errors
    
    @staticmethod
    def validate_stress_tester(instance) -> List[str]:
        """驗證壓力測試器是否符合接口契約"""
        errors = []
        
        required_methods = ['calculate_statistics', 'validate_test_config']
        
        for method in required_methods:
            if not hasattr(instance, method):
                errors.append(f"缺少必要方法: {method}")
            elif not callable(getattr(instance, method)):
                errors.append(f"方法不可調用: {method}")
        
        return errors

# ========== 測試數據契約 ==========

class TestDataContract:
    """測試數據格式契約"""
    
    USER_SCHEMA = {
        'id': str,
        'username': str,
        'email': str,
        'role': str,
        'created_at': str
    }
    
    TEST_CASE_SCHEMA = {
        'id': int,
        'tc_id': str,
        'title': str,
        'description': str,
        'priority': str,
        'status': str
    }
    
    STATISTICS_SCHEMA = {
        'total': int,
        'by_status': dict,
        'by_priority': dict
    }
    
    @staticmethod
    def validate_data_schema(data: Dict, schema: Dict) -> List[str]:
        """驗證數據是否符合預期格式"""
        errors = []
        
        for field, expected_type in schema.items():
            if field not in data:
                errors.append(f"缺少必要欄位: {field}")
            elif not isinstance(data[field], expected_type):
                errors.append(f"欄位類型錯誤: {field} 應為 {expected_type.__name__}")
        
        return errors