# Gunicorn 生產環境配置文件

import os
import multiprocessing

# 服務器設置
bind = f"0.0.0.0:{os.getenv('PORT', 5001)}"
workers = int(os.getenv('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 30
keepalive = 2

# 日誌設置
accesslog = '/app/logs/gunicorn-access.log'
errorlog = '/app/logs/gunicorn-error.log'
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 進程設置
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = 1000
group = 1000
tmp_upload_dir = None

# 性能設置
worker_tmp_dir = "/dev/shm"
capture_output = True
enable_stdio_inheritance = True

# 安全設置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL 設置 (如果需要)
# keyfile = "/app/ssl/key.pem"
# certfile = "/app/ssl/cert.pem"

# 生命週期函數
def on_starting(server):
    """服務器啟動時調用"""
    server.log.info("Starting API Monitor with Gunicorn")

def on_reload(server):
    """重載時調用"""
    server.log.info("Reloading API Monitor")

def worker_int(worker):
    """工作進程收到 SIGINT 信號時調用"""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """工作進程 fork 前調用"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """工作進程 fork 後調用"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    """工作進程異常終止時調用"""
    worker.log.info("Worker received SIGABRT signal")