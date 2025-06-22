# 使用官方 Python 3.11 slim 基礎鏡像
FROM python:3.11-slim as base

# 設置工作目錄
WORKDIR /app

# 設置環境變量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=simple_app.py \
    FLASK_ENV=production

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

# 創建數據庫初始化腳本並執行
RUN python railway_init.py

# 暴露端口（Railway 會動態分配）
EXPOSE ${PORT:-5001}

# 創建非 root 用戶
RUN adduser --disabled-password --gecos '' --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# 健康檢查（移除，因為 Railway 有自己的健康檢查機制）
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:${PORT:-5001}/health || exit 1

# 啟動命令
CMD ["python", "simple_app.py"]