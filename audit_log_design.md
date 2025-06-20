# 操作記錄系統設計文檔

## 1. 數據模型設計

### AuditLog 模型

```python
@dataclass
class AuditLog:
    """操作記錄模型"""
    id: str                           # 記錄ID
    user_id: str                      # 操作用戶ID
    username: str                     # 操作用戶名（冗余存儲，便於查詢）
    action_type: ActionType           # 操作類型枚舉
    resource_type: ResourceType       # 資源類型枚舉
    resource_id: Optional[str]        # 資源ID（如果適用）
    resource_name: Optional[str]      # 資源名稱（便於顯示）
    description: str                  # 操作描述
    old_values: Optional[Dict]        # 變更前的數據
    new_values: Optional[Dict]        # 變更後的數據
    changes: Optional[Dict]           # 變更差異（結構化）
    ip_address: Optional[str]         # 操作者IP地址
    user_agent: Optional[str]         # 用戶代理字串
    status: ActionStatus              # 操作狀態（成功/失敗）
    error_message: Optional[str]      # 錯誤信息（如果失敗）
    session_id: Optional[str]         # 會話ID
    timestamp: datetime               # 操作時間
    duration_ms: Optional[int]        # 操作耗時（毫秒）
```

### 枚舉定義

```python
class ActionType(Enum):
    """操作類型"""
    CREATE = "create"           # 新增
    UPDATE = "update"           # 更新
    DELETE = "delete"           # 刪除
    LOGIN = "login"             # 登入
    LOGOUT = "logout"           # 登出
    EXPORT = "export"           # 導出
    IMPORT = "import"           # 導入
    EXECUTE = "execute"         # 執行測試
    ACCESS = "access"           # 訪問

class ResourceType(Enum):
    """資源類型"""
    USER = "user"               # 用戶
    TEST_CASE = "test_case"     # 測試案例
    TEST_PROJECT = "test_project" # 測試專案
    PRODUCT_TAG = "product_tag" # 產品標籤
    API_ENDPOINT = "api_endpoint" # API端點
    TEST_RESULT = "test_result" # 測試結果
    SYSTEM = "system"           # 系統

class ActionStatus(Enum):
    """操作狀態"""
    SUCCESS = "success"         # 成功
    FAILED = "failed"          # 失敗
    PARTIAL = "partial"        # 部分成功
```

## 2. 需要記錄的操作範圍

### 2.1 用戶管理
- 用戶登入/登出
- 新增用戶
- 編輯用戶信息
- 刪除用戶
- 用戶角色變更

### 2.2 測試案例管理
- 新增測試案例
- 編輯測試案例
- 刪除測試案例
- 批量操作測試案例
- 測試案例狀態變更

### 2.3 測試專案管理
- 新增測試專案
- 編輯測試專案
- 刪除測試專案
- 專案狀態變更
- 指派/取消指派測試案例

### 2.4 產品標籤管理
- 新增產品標籤
- 編輯產品標籤
- 刪除產品標籤

### 2.5 測試執行
- 執行測試
- 更新測試結果
- 測試狀態變更

### 2.6 系統管理
- API配置變更
- 系統設置變更

### 2.7 數據操作
- 導入/導出操作
- 批量數據處理

## 3. 變更差異記錄機制

### 3.1 字段級別差異追蹤
```python
def calculate_changes(old_data: Dict, new_data: Dict) -> Dict:
    """計算變更差異"""
    changes = {}
    
    # 檢查所有字段
    all_keys = set(old_data.keys()) | set(new_data.keys())
    
    for key in all_keys:
        old_value = old_data.get(key)
        new_value = new_data.get(key)
        
        if old_value != new_value:
            changes[key] = {
                'old': old_value,
                'new': new_value,
                'action': determine_action(old_value, new_value)
            }
    
    return changes

def determine_action(old_value, new_value):
    """確定變更動作"""
    if old_value is None:
        return 'added'
    elif new_value is None:
        return 'removed'
    else:
        return 'modified'
```

### 3.2 敏感資料處理
- 密碼等敏感資料不記錄實際值
- 使用 `[REDACTED]` 或 `[SENSITIVE]` 標記
- 記錄敏感欄位是否發生變更

## 4. 數據庫結構設計

### SQLite 表結構
```sql
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    action_type TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    resource_name TEXT,
    description TEXT NOT NULL,
    old_values TEXT,          -- JSON字串
    new_values TEXT,          -- JSON字串
    changes TEXT,             -- JSON字串
    ip_address TEXT,
    user_agent TEXT,
    status TEXT NOT NULL,
    error_message TEXT,
    session_id TEXT,
    timestamp DATETIME NOT NULL,
    duration_ms INTEGER,
    
    -- 索引優化
    INDEX idx_audit_user_id (user_id),
    INDEX idx_audit_timestamp (timestamp),
    INDEX idx_audit_action_type (action_type),
    INDEX idx_audit_resource_type (resource_type),
    INDEX idx_audit_resource_id (resource_id)
);
```

## 5. 前端查看界面設計

### 5.1 主界面佈局
- 側邊欄新增「操作記錄」菜單項（僅管理員可見）
- 表格形式顯示記錄列表
- 支持分頁和搜索過濾

### 5.2 過濾功能
- 按用戶過濾
- 按操作類型過濾
- 按資源類型過濾
- 按時間範圍過濾
- 按操作狀態過濾

### 5.3 詳情查看
- 點擊記錄查看詳細信息
- 變更前後對比視圖
- 支持JSON格式化顯示

### 5.4 界面設計要素
```html
<!-- 操作記錄頁面佈局 -->
<div class="audit-log-container">
    <!-- 過濾器區域 -->
    <div class="filter-section">
        <div class="filter-row">
            <select id="userFilter">用戶過濾</select>
            <select id="actionFilter">操作類型</select>
            <select id="resourceFilter">資源類型</select>
            <input type="date" id="dateFrom">
            <input type="date" id="dateTo">
            <button onclick="applyFilters()">應用過濾</button>
        </div>
    </div>
    
    <!-- 記錄列表 -->
    <div class="audit-table-container">
        <table class="audit-table">
            <thead>
                <tr>
                    <th>時間</th>
                    <th>用戶</th>
                    <th>操作</th>
                    <th>資源</th>
                    <th>狀態</th>
                    <th>詳情</th>
                </tr>
            </thead>
            <tbody id="auditTableBody">
                <!-- 動態生成 -->
            </tbody>
        </table>
    </div>
    
    <!-- 分頁 -->
    <div class="pagination-container">
        <!-- 分頁控件 -->
    </div>
</div>

<!-- 詳情模態框 -->
<div class="audit-detail-modal">
    <div class="detail-content">
        <div class="detail-header">操作詳情</div>
        <div class="detail-body">
            <!-- 基本信息 -->
            <div class="detail-section">
                <h4>基本信息</h4>
                <div class="detail-info">...</div>
            </div>
            
            <!-- 變更詳情 -->
            <div class="detail-section">
                <h4>變更內容</h4>
                <div class="changes-view">
                    <!-- 變更前後對比 -->
                </div>
            </div>
        </div>
    </div>
</div>
```

## 6. 實現架構設計

### 6.1 核心組件

#### AuditLogger 類
```python
class AuditLogger:
    """審計日誌記錄器"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def log_action(self, user_id: str, action_type: ActionType, 
                   resource_type: ResourceType, **kwargs):
        """記錄操作"""
        pass
    
    def log_create(self, user_id: str, resource_type: ResourceType, 
                   resource_data: Dict):
        """記錄新增操作"""
        pass
    
    def log_update(self, user_id: str, resource_type: ResourceType,
                   resource_id: str, old_data: Dict, new_data: Dict):
        """記錄更新操作"""
        pass
    
    def log_delete(self, user_id: str, resource_type: ResourceType,
                   resource_id: str, resource_data: Dict):
        """記錄刪除操作"""
        pass
```

#### 裝飾器模式
```python
def audit_log(action_type: ActionType, resource_type: ResourceType):
    """審計日誌裝飾器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 記錄操作前的狀態
            # 執行原函數
            # 記錄操作後的狀態
            # 寫入審計日誌
            pass
        return wrapper
    return decorator
```

#### 中間件集成
```python
class AuditMiddleware:
    """審計中間件"""
    
    def __init__(self, app, audit_logger):
        self.app = app
        self.audit_logger = audit_logger
        self.setup_middleware()
    
    def setup_middleware(self):
        """設置中間件"""
        # 在請求前後記錄相關信息
        pass
```

### 6.2 集成點

1. **路由層面**：在API路由中添加審計裝飾器
2. **服務層面**：在業務邏輯層記錄操作
3. **中間件層面**：全局攔截請求進行記錄

### 6.3 配置管理
```python
# 審計配置
AUDIT_CONFIG = {
    'enabled': True,
    'log_levels': ['create', 'update', 'delete'],
    'excluded_resources': [],
    'sensitive_fields': ['password', 'token', 'secret'],
    'retention_days': 365,
    'max_records_per_page': 50
}
```

## 7. 性能考慮

### 7.1 異步記錄
- 使用隊列機制異步寫入審計日誌
- 避免影響主業務邏輯性能

### 7.2 數據清理
- 定期清理過期記錄
- 數據歸檔機制

### 7.3 索引優化
- 關鍵查詢字段建立索引
- 分頁查詢優化

## 8. 安全考慮

### 8.1 權限控制
- 僅管理員可查看操作記錄
- 記錄訪問本身也需要審計

### 8.2 數據保護
- 敏感數據脫敏處理
- 傳輸加密

### 8.3 防篡改
- 審計記錄一旦寫入不可修改
- 數據完整性校驗

## 9. 實施計劃

### Phase 1: 核心功能
1. 數據模型和數據庫表創建
2. AuditLogger 核心類實現
3. 基本的記錄功能

### Phase 2: 集成
1. 在現有API中集成審計功能
2. 裝飾器和中間件實現
3. 前端查看界面

### Phase 3: 優化
1. 性能優化
2. 高級過濾功能
3. 數據清理和歸檔

## 10. API 設計

### 查看操作記錄
```
GET /api/audit-logs
參數：
- page: 頁碼
- limit: 每頁記錄數
- user_id: 用戶ID過濾
- action_type: 操作類型過濾
- resource_type: 資源類型過濾
- date_from: 開始日期
- date_to: 結束日期
- status: 狀態過濾
```

### 獲取單個記錄詳情
```
GET /api/audit-logs/{log_id}
```

### 獲取統計信息
```
GET /api/audit-logs/statistics
返回：用戶活動統計、操作類型分布等
```