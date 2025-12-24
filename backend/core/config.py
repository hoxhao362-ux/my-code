from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_core(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # 允许哪些来源的跨域请求，生产环境要指定具体域名，比如["http://localhost:3000", "https://your-front.com"]）
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

APP_VERSION = "dev"
APP_NAME = "期刊平台"
LOCAL_HOST = "localhost"
PORT = 8000
