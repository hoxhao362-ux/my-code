import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator

class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(
        ...,
        description="密码规则：8-20位，含大小写字母+数字，可使用!@#$%^&*()_+-={}[]:;'\"<>,.?~`等特殊字符，禁止|\\/和中文",
        min_length=8,
        max_length=20
    )
    is_remember: bool = Field(False, description="是否记住登录状态")

class LoginResponse(BaseModel):
    login_time: datetime.datetime = Field(default_factory=datetime.datetime.now, description="登录时间")
    is_remember: bool = Field(False, description="是否记住登录状态")
    token: str = Field(..., description="登录凭证")
    message: str = Field(..., description="登录返回的消息")

class RegisterRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(
        ...,
        description="密码规则：8-20位，含大小写字母+数字，可使用!@#$%^&*()_+-={}[]:;'\"<>,.?~`等特殊字符，禁止|\\/和中文",
        min_length=8,
        max_length=20
    )
    email: EmailStr = Field(..., description="注册邮箱")
    invite_code: None | str = Field(None, description="邀请码(选填)")

class RegisterResponse(BaseModel):
    register_time: datetime.datetime = Field(default_factory=datetime.datetime.now, description="注册时间")
    token: str = Field(..., description="登录凭证")
    message: str = Field(..., description="注册返回的消息")

class RoleUpgradeRequest(BaseModel):
    invite_code: str = Field(..., description="邀请码")
