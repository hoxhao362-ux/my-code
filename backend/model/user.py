import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def validate_sha256_hash(v: str) -> str:
    """
    校验密码为有效的 SHA256 哈希字符串（64 字符十六进制）

    前端传入的密码已进行 SHA256 加密处理，固定为 64 字符十六进制字符串。
    此校验器用于 RegisterRequest / LoginRequest / ChangePasswordRequest 中的密码字段复用。

    Args:
        v: 待校验的密码字符串

    Returns:
        str: 统一转为小写的 SHA256 哈希字符串

    Raises:
        ValueError: 密码格式不符合 SHA256 哈希要求
    """
    if not isinstance(v, str) or len(v) != 64:
        raise ValueError("密码格式无效：应为 64 字符的 SHA256 哈希")
    try:
        int(v, 16)  # 验证是合法十六进制
    except ValueError:
        raise ValueError("密码格式无效：应为十六进制字符串")
    return v.lower()  # 统一小写


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(
        ...,
        description="密码（SHA256 哈希，64 字符十六进制字符串）",
    )
    is_remember: bool = Field(False, description="是否记住登录状态")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """校验密码为有效的 SHA256 哈希"""
        return validate_sha256_hash(v)


class LoginResponse(BaseModel):
    login_time: datetime.datetime = Field(
        default_factory=datetime.datetime.now, description="登录时间"
    )
    is_remember: bool = Field(False, description="是否记住登录状态")
    token: str = Field(..., description="登录凭证")
    message: str = Field(..., description="登录返回的消息")


class RegisterRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(
        ...,
        description="密码（SHA256 哈希，64 字符十六进制字符串）",
    )
    email: EmailStr = Field(..., description="注册邮箱")
    invite_code: None | str = Field(None, description="邀请码(选填)")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """校验密码为有效的 SHA256 哈希"""
        return validate_sha256_hash(v)


class RegisterResponse(BaseModel):
    register_time: datetime.datetime = Field(
        default_factory=datetime.datetime.now, description="注册时间"
    )
    token: str = Field(..., description="登录凭证")
    message: str = Field(..., description="注册返回的消息")


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""

    old_password: str = Field(..., description="旧密码（SHA256 哈希）")
    new_password: str = Field(..., description="新密码（SHA256 哈希）")

    @field_validator("old_password", "new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """校验密码为有效的 SHA256 哈希"""
        return validate_sha256_hash(v)


class RoleUpgradeRequest(BaseModel):
    invite_code: str = Field(..., description="邀请码")


class UserProfileDTO(BaseModel):
    """
    用户信息 DTO

    用于用户信息接口返回，从 User ORM 对象或字段字典转换。
    支持 model_validate(orm_object) 或 model_validate(dict) 两种构造方式。
    """

    model_config = ConfigDict(from_attributes=True)

    uid: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    role: str = Field(..., description="角色")
    is_verified: bool = Field(default=False, description="是否已验证")
    create_time: Optional[str] = Field(None, description="创建时间")
    last_login_time: Optional[str] = Field(None, description="最后登录时间")
    avatar_hash: Optional[str] = Field(None, description="头像哈希")
