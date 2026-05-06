FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    PATH="/app/.venv/bin:$PATH" \
    TZ=Asia/Shanghai

# 安装系统依赖（如需编译部分Python包）及 LibreOffice 与中文字体
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libreoffice-core \
    libreoffice-writer \
    fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*

# 复制 uv 依赖描述文件并安装（与开发环境锁文件保持一致）
COPY pyproject.toml uv.lock README.md /app/
RUN pip install --no-cache-dir uv && \
    uv sync --frozen --no-dev --no-install-project

# 复制项目代码
COPY . /app/

# 暴露端口
EXPOSE 8000

# 使用 Gunicorn + Uvicorn Worker 启动应用
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
