FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

# 安装系统依赖（如需编译部分Python包）及 LibreOffice 与中文字体
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libreoffice-core \
    libreoffice-writer \
    fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . /app/

# 暴露端口
EXPOSE 8000

# 使用 Gunicorn 启动应用
CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]
