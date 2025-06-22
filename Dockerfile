# 使用官方 Python 3.11 slim 基礎鏡像
FROM python:3.11-slim as base

# 設置工作目錄
WORKDIR /app

# 設置環境變量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=simple_app.py \
    FLASK_ENV=production \
    PORT=5001

# 安裝系統依賴
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libc6-dev \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建數據目錄並設置權限
RUN mkdir -p /app/data \
    && mkdir -p /app/logs \
    && chmod -R 755 /app/data \
    && chmod -R 755 /app/logs

# 初始化數據庫（如果不存在）
RUN python -c "
from database.db_manager import db_manager
import os

# 檢查數據庫是否存在，如果不存在則創建
if not os.path.exists('/app/data/api_monitor.db'):
    print('初始化數據庫...')
    db_manager.init_database()
    print('數據庫初始化完成')
else:
    print('數據庫已存在')
"

# 暴露端口
EXPOSE 5001

# 創建非 root 用戶
RUN adduser --disabled-password --gecos '' --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# 啟動命令
CMD ["python", "simple_app.py"]