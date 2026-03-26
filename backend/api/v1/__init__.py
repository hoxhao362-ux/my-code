"""
API v1 版本初始化

包含所有 v1 版本的 API 路由模块
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .manuscripts import router as manuscripts_router
from .reviews import router as reviews_router
from .editorial import router as editorial_router
from .admin import admin_router
from .public import router as public_router

# 创建 v1 版本的路由器
v1_router = APIRouter(prefix="/api/v1")

# 注册所有子模块路由
v1_router.include_router(auth_router)
v1_router.include_router(users_router)
v1_router.include_router(manuscripts_router)
v1_router.include_router(reviews_router)
v1_router.include_router(editorial_router)
v1_router.include_router(admin_router)
v1_router.include_router(public_router)
