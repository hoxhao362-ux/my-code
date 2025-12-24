from fastapi import APIRouter, HTTPException

from utils import database, text, time

from model.user import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse

user_router = APIRouter(
    prefix="/user",
    tags=["用户相关接口"],
)

@user_router.post("/login", summary="用户登录")
async def login(request: LoginRequest):
    return {"message": "登录成功"}

@user_router.post("/register", summary="用户注册")
async def register(request: RegisterRequest):
    return {"message": "注册成功"}