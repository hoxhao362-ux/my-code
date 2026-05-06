"""
[DEPRECATED] 用户相关API接口

本模块已废弃，请勿在新代码中使用。
迁移指引：
- 用户认证功能（注册、登录、登出、修改密码）请使用 auth.py 中的接口。
- 用户管理功能（获取信息、修改信息、角色管理等）请使用 users.py 中的接口。
- 本文件路由已全部移除，以避免旧版本接口继续被调用。

旧角色名映射：
- 'normal' -> 'user' (UserRole.USER)
- 'writer' -> 'author' (UserRole.AUTHOR)

废弃日期：2026-03-26
保留原因：向后兼容说明
"""
from fastapi import APIRouter

# 创建空的用户相关路由，避免导入错误
user_router = APIRouter(
    prefix="/user",
    tags=["[已废弃] 用户相关接口"],
    deprecated=True
)