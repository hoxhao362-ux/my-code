import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator

class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(
        ...,
        description="密码规则：8-20位，含大小写字母+数字，可使用!@#$%^&*()_+-={}[]:;'\"<>,.?~`等特殊字符，禁止|\/和中文",
        min_length=8,
        max_length=20
    )
    is_remember: bool = Field(False, description="是否记住登录状态")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """自定义密码验证"""
        # 检查是否包含小写字母
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含小写字母')
        # 检查是否包含大写字母
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含大写字母')
        # 检查是否包含数字
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含数字')
        # 检查是否包含禁止字符
        if any(c in '|\/' or ord(c) > 127 for c in v):
            raise ValueError('密码不能包含|\/和中文')
        return v

class LoginResponse(BaseModel):
    login_time: datetime.datetime = Field(default_factory=datetime.datetime.now, description="登录时间")
    is_remember: bool = Field(False, description="是否记住登录状态")
    token: str = Field(..., description="登录凭证")

class RegisterRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(
        ...,
        description="密码规则：8-20位，含大小写字母+数字，可使用!@#$%^&*()_+-={}[]:;'\"<>,.?~`等特殊字符，禁止|\/和中文",
        min_length=8,
        max_length=20
    )
    email: EmailStr = Field(..., description="注册邮箱")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """自定义密码验证"""
        # 检查是否包含小写字母
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含小写字母')
        # 检查是否包含大写字母
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含大写字母')
        # 检查是否包含数字
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含数字')
        # 检查是否包含禁止字符
        if any(c in '|\/' or ord(c) > 127 for c in v):
            raise ValueError('密码不能包含|\/和中文')
        return v

class RegisterResponse(BaseModel):
    register_time: datetime.datetime = Field(default_factory=datetime.datetime.now, description="注册时间")
    token: str = Field(..., description="登录凭证")
