import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DATA_FILE = 'data/apis.json'
    CHECK_INTERVAL = 60  # 檢查間隔（秒）
    MAX_ERROR_COUNT = 3  # 連續錯誤次數閾值
    REQUEST_TIMEOUT = 10  # HTTP 請求超時時間（秒）