import multiprocessing
import os

# 绑定地址与端口
bind = "0.0.0.0:8000"

# 使用 UvicornWorker 提供异步能力
worker_class = "uvicorn.workers.UvicornWorker"

# Worker 数量
# 可以通过环境变量 WORKERS 覆盖，否则默认使用 CPU_COUNT * 2 + 1
workers_env = os.getenv("WORKERS")
if workers_env and workers_env.isdigit():
    workers = int(workers_env)
else:
    workers = multiprocessing.cpu_count() * 2 + 1

# 最大并发连接数
worker_connections = 1000

# 超时时间（秒）
timeout = 120

# 保持存活时间（秒）
keepalive = 5

# 日志配置
# "-" 表示输出到标准输出，Docker 会自动收集
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

# 真实 IP 配置，让 Gunicorn 信任 Nginx 等代理转发的头部
forwarded_allow_ips = "*"
proxy_allow_ips = "*"
