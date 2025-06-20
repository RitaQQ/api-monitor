import uuid
import json
from datetime import datetime
from typing import List, Dict, Optional
from database.db_manager import db_manager

class DataManager:
    """基於 SQLite 的資料管理器"""
    
    def __init__(self, data_file: str = None):
        """
        初始化資料管理器
        
        Args:
            data_file: 為了向後兼容保留此參數，但實際使用 SQLite
        """
        # 向後兼容，但實際上使用 SQLite
        pass
    
    def load_apis(self) -> List[Dict]:
        """載入 API 清單"""
        query = """
            SELECT 
                id, name, url, type, method, request_body,
                status, response_time, last_check, error_count, 
                last_error, last_response,
                concurrent_requests, duration_seconds, interval_seconds,
                created_at, updated_at
            FROM apis 
            ORDER BY created_at DESC
        """
        apis = db_manager.execute_query(query)
        
        # 為每個 API 添加 stress_test 配置（保持向後兼容）
        for api in apis:
            api['stress_test'] = {
                'concurrent_requests': api.get('concurrent_requests', 1),
                'duration_seconds': api.get('duration_seconds', 10),
                'interval_seconds': api.get('interval_seconds', 1.0),
                'enabled': False,
                'last_test': self._get_last_stress_test_time(api['id']),
                'results': self._get_stress_test_results(api['id'])
            }
        
        return apis
    
    def save_apis(self, apis: List[Dict]):
        """儲存 API 清單（向後兼容方法，實際不建議使用）"""
        # 這個方法保留是為了向後兼容，但建議使用個別的 add/update/delete 方法
        pass
    
    def add_api(self, name: str, url: str, api_type: str = "REST", method: str = "GET", 
                request_body: str = None, concurrent_requests: int = 1, 
                duration_seconds: int = 10, interval_seconds: float = 1.0) -> Dict:
        """新增 API"""
        api_id = str(uuid.uuid4())
        
        query = """
            INSERT INTO apis (
                id, name, url, type, method, request_body,
                concurrent_requests, duration_seconds, interval_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        db_manager.execute_insert(query, (
            api_id, name, url, api_type, method, request_body,
            concurrent_requests, duration_seconds, interval_seconds
        ))
        
        # 返回新創建的 API
        return self.get_api_by_id(api_id)
    
    def delete_api(self, api_id: str) -> bool:
        """刪除 API"""
        query = "DELETE FROM apis WHERE id = ?"
        rows_affected = db_manager.execute_delete(query, (api_id,))
        return rows_affected > 0
    
    def update_api_status(self, api_id: str, status: str, response_time: float = 0, 
                         error_msg: str = None, response_data: str = None):
        """更新 API 狀態"""
        query = """
            UPDATE apis 
            SET status = ?, response_time = ?, last_check = ?, 
                last_response = ?, error_count = CASE 
                    WHEN ? = 'unhealthy' THEN error_count + 1 
                    ELSE 0 
                END,
                last_error = CASE 
                    WHEN ? = 'unhealthy' THEN ? 
                    ELSE NULL 
                END
            WHERE id = ?
        """
        
        db_manager.execute_update(query, (
            status, response_time, datetime.now().isoformat(),
            response_data, status, status, error_msg, api_id
        ))
    
    def get_api_by_id(self, api_id: str) -> Optional[Dict]:
        """根據 ID 取得特定 API"""
        query = """
            SELECT 
                id, name, url, type, method, request_body,
                status, response_time, last_check, error_count, 
                last_error, last_response,
                concurrent_requests, duration_seconds, interval_seconds,
                created_at, updated_at
            FROM apis 
            WHERE id = ?
        """
        results = db_manager.execute_query(query, (api_id,))
        
        if results:
            api = results[0]
            # 添加 stress_test 配置
            api['stress_test'] = {
                'concurrent_requests': api.get('concurrent_requests', 1),
                'duration_seconds': api.get('duration_seconds', 10),
                'interval_seconds': api.get('interval_seconds', 1.0),
                'enabled': False,
                'last_test': self._get_last_stress_test_time(api['id']),
                'results': self._get_stress_test_results(api['id'])
            }
            return api
        
        return None
    
    def update_stress_test_config(self, api_id: str, concurrent_requests: int, 
                                 duration_seconds: int, interval_seconds: float, 
                                 enabled: bool = False):
        """更新壓力測試配置"""
        query = """
            UPDATE apis 
            SET concurrent_requests = ?, duration_seconds = ?, interval_seconds = ?
            WHERE id = ?
        """
        
        db_manager.execute_update(query, (
            concurrent_requests, duration_seconds, interval_seconds, api_id
        ))
    
    def save_stress_test_result(self, api_id: str, result: Dict):
        """儲存壓力測試結果"""
        query = """
            INSERT INTO stress_test_results (
                api_id, test_name, start_time, end_time,
                total_requests, successful_requests, failed_requests,
                success_rate, avg_response_time, min_response_time,
                max_response_time, requests_per_second,
                test_config, raw_results
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # 提取統計信息
        stats = result.get('statistics', {})
        
        db_manager.execute_insert(query, (
            api_id,
            result.get('test_name', f"Test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            result.get('start_time'),
            result.get('end_time'),
            stats.get('total_requests', 0),
            stats.get('successful_requests', 0),
            stats.get('failed_requests', 0),
            stats.get('success_rate', 0.0),
            stats.get('avg_response_time', 0.0),
            stats.get('min_response_time', 0.0),
            stats.get('max_response_time', 0.0),
            stats.get('requests_per_second', 0.0),
            json.dumps(result.get('config', {})),
            json.dumps(result)
        ))
        
        # 只保留最近 10 次測試結果
        self._cleanup_old_stress_test_results(api_id)
    
    def update_api(self, api_id: str, name: str, url: str, api_type: str = "REST", 
                   method: str = "GET", request_body: str = None, 
                   concurrent_requests: int = 1, duration_seconds: int = 10, 
                   interval_seconds: float = 1.0) -> bool:
        """更新 API 資訊"""
        query = """
            UPDATE apis 
            SET name = ?, url = ?, type = ?, method = ?, request_body = ?,
                concurrent_requests = ?, duration_seconds = ?, interval_seconds = ?,
                status = 'unknown', response_time = 0, last_check = NULL,
                error_count = 0, last_error = NULL
            WHERE id = ?
        """
        
        rows_affected = db_manager.execute_update(query, (
            name, url, api_type, method, request_body,
            concurrent_requests, duration_seconds, interval_seconds,
            api_id
        ))
        
        return rows_affected > 0
    
    def _get_last_stress_test_time(self, api_id: str) -> Optional[str]:
        """獲取最後一次壓力測試時間"""
        query = """
            SELECT start_time FROM stress_test_results 
            WHERE api_id = ? 
            ORDER BY start_time DESC 
            LIMIT 1
        """
        results = db_manager.execute_query(query, (api_id,))
        return results[0]['start_time'] if results else None
    
    def _get_stress_test_results(self, api_id: str, limit: int = 10) -> List[Dict]:
        """獲取壓力測試結果"""
        query = """
            SELECT 
                test_name, start_time, end_time,
                total_requests, successful_requests, failed_requests,
                success_rate, avg_response_time, min_response_time,
                max_response_time, requests_per_second,
                raw_results
            FROM stress_test_results 
            WHERE api_id = ? 
            ORDER BY start_time DESC 
            LIMIT ?
        """
        results = db_manager.execute_query(query, (api_id, limit))
        
        # 解析 raw_results JSON
        for result in results:
            if result['raw_results']:
                try:
                    raw_data = json.loads(result['raw_results'])
                    result['requests'] = raw_data.get('requests', [])
                    result['statistics'] = {
                        'total_requests': result['total_requests'],
                        'successful_requests': result['successful_requests'],
                        'failed_requests': result['failed_requests'],
                        'success_rate': result['success_rate'],
                        'avg_response_time': result['avg_response_time'],
                        'min_response_time': result['min_response_time'],
                        'max_response_time': result['max_response_time'],
                        'requests_per_second': result['requests_per_second']
                    }
                except json.JSONDecodeError:
                    result['requests'] = []
                    result['statistics'] = {}
        
        return results
    
    def _cleanup_old_stress_test_results(self, api_id: str, keep_count: int = 10):
        """清理舊的壓力測試結果"""
        query = """
            DELETE FROM stress_test_results 
            WHERE api_id = ? AND id NOT IN (
                SELECT id FROM stress_test_results 
                WHERE api_id = ? 
                ORDER BY start_time DESC 
                LIMIT ?
            )
        """
        db_manager.execute_delete(query, (api_id, api_id, keep_count))
    
    def get_api_statistics(self) -> Dict:
        """獲取 API 統計信息"""
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'healthy' THEN 1 ELSE 0 END) as healthy,
                SUM(CASE WHEN status = 'unhealthy' THEN 1 ELSE 0 END) as unhealthy,
                SUM(CASE WHEN status = 'unknown' THEN 1 ELSE 0 END) as unknown
            FROM apis
        """
        results = db_manager.execute_query(query)
        return results[0] if results else {'total': 0, 'healthy': 0, 'unhealthy': 0, 'unknown': 0}