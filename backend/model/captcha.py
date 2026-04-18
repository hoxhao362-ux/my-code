"""
验证码相关数据模型

定义验证码相关的请求和响应 Pydantic 模型
"""

from pydantic import BaseModel, Field


class CaptchaVerifyRequest(BaseModel):
    """图形验证码校验请求参数模型"""

    req_id: str = Field(
        ...,
        description="获取验证码时返回的唯一请求ID",
        example="123e4567e89b12d3a456426614174000",
    )
    code: str = Field(
        ..., description="用户输入的验证码文本（不区分大小写）", example="aB3d"
    )
