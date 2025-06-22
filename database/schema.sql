-- API 監控系統資料庫結構

-- 用戶表
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- API 表
CREATE TABLE IF NOT EXISTS apis (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    type TEXT DEFAULT 'REST',
    method TEXT DEFAULT 'GET',
    request_body TEXT,
    status TEXT DEFAULT 'unknown',
    response_time REAL DEFAULT 0,
    last_check DATETIME,
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    last_response TEXT,
    concurrent_requests INTEGER DEFAULT 1,
    duration_seconds INTEGER DEFAULT 10,
    interval_seconds REAL DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 壓力測試結果表
CREATE TABLE IF NOT EXISTS stress_test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_id TEXT NOT NULL,
    test_name TEXT,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0,
    avg_response_time REAL DEFAULT 0.0,
    min_response_time REAL DEFAULT 0.0,
    max_response_time REAL DEFAULT 0.0,
    requests_per_second REAL DEFAULT 0.0,
    test_config TEXT, -- JSON 格式儲存測試配置
    raw_results TEXT, -- JSON 格式儲存原始結果
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (api_id) REFERENCES apis (id) ON DELETE CASCADE
);

-- 產品標籤表
CREATE TABLE IF NOT EXISTS product_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    color TEXT DEFAULT '#007bff',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 測試專案表
CREATE TABLE IF NOT EXISTS test_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'draft',
    responsible_user_id TEXT,
    start_time DATETIME,
    end_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (responsible_user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- 測試案例表
CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tc_id TEXT UNIQUE NOT NULL, -- TC00001 格式的 ID
    title TEXT NOT NULL,
    description TEXT,
    acceptance_criteria TEXT,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'draft',
    test_project_id INTEGER,
    responsible_user_id TEXT,
    estimated_hours REAL DEFAULT 0,
    actual_hours REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_project_id) REFERENCES test_projects (id) ON DELETE SET NULL,
    FOREIGN KEY (responsible_user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- 測試案例與產品標籤關聯表
CREATE TABLE IF NOT EXISTS test_case_tags (
    test_case_id INTEGER NOT NULL,
    product_tag_id INTEGER NOT NULL,
    PRIMARY KEY (test_case_id, product_tag_id),
    FOREIGN KEY (test_case_id) REFERENCES test_cases (id) ON DELETE CASCADE,
    FOREIGN KEY (product_tag_id) REFERENCES product_tags (id) ON DELETE CASCADE
);

-- 測試結果表
CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    test_case_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'not_tested',
    notes TEXT,
    known_issues TEXT,
    blocked_reason TEXT,
    tested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES test_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
    UNIQUE(project_id, test_case_id)
);

-- 用戶故事表（向後兼容）
CREATE TABLE IF NOT EXISTS user_stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    project_name TEXT,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 創建索引以提升查詢效能
CREATE INDEX IF NOT EXISTS idx_apis_status ON apis(status);
CREATE INDEX IF NOT EXISTS idx_apis_url ON apis(url);
CREATE INDEX IF NOT EXISTS idx_stress_test_results_api_id ON stress_test_results(api_id);
CREATE INDEX IF NOT EXISTS idx_stress_test_results_start_time ON stress_test_results(start_time);
CREATE INDEX IF NOT EXISTS idx_test_cases_tc_id ON test_cases(tc_id);
CREATE INDEX IF NOT EXISTS idx_test_cases_status ON test_cases(status);
CREATE INDEX IF NOT EXISTS idx_test_cases_project_id ON test_cases(test_project_id);
CREATE INDEX IF NOT EXISTS idx_test_results_project ON test_results(project_id);
CREATE INDEX IF NOT EXISTS idx_test_results_test_case ON test_results(test_case_id);
CREATE INDEX IF NOT EXISTS idx_test_results_status ON test_results(status);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- 創建觸發器自動更新 updated_at 欄位
CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
    AFTER UPDATE ON users
    BEGIN
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_apis_timestamp 
    AFTER UPDATE ON apis
    BEGIN
        UPDATE apis SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_product_tags_timestamp 
    AFTER UPDATE ON product_tags
    BEGIN
        UPDATE product_tags SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_test_projects_timestamp 
    AFTER UPDATE ON test_projects
    BEGIN
        UPDATE test_projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_test_cases_timestamp 
    AFTER UPDATE ON test_cases
    BEGIN
        UPDATE test_cases SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_test_results_timestamp 
    AFTER UPDATE ON test_results
    BEGIN
        UPDATE test_results SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- 操作記錄表
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    action TEXT NOT NULL,           -- 操作類型：CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    resource_type TEXT NOT NULL,    -- 資源類型：USER, API, TEST_CASE, TEST_PROJECT
    resource_id TEXT,              -- 資源ID
    resource_name TEXT,            -- 資源名稱
    old_values TEXT,               -- 變更前內容（JSON格式）
    new_values TEXT,               -- 變更後內容（JSON格式）
    ip_address TEXT,               -- 操作者IP
    user_agent TEXT,               -- 瀏覽器信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 操作記錄索引
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);