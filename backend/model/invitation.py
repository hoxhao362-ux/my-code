"""
邀请码相关数据模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class InvitationCodeCreateRequest(BaseModel):
    """创建邀请码请求模型"""
    role: str = Field(..., description="邀请码对应的角色", pattern="^(admin|reviewer|writer|normal)$")
    description: Optional[str] = Field(None, description="邀请码描述")
    max_uses: Optional[int] = Field(1, description="最大使用次数，默认为1")
    expire_time: Optional[datetime] = Field(None, description="过期时间")

class InvitationCodeResponse(BaseModel):
    """邀请码响应模型"""
    code: str = Field(..., description="邀请码")
    role: str = Field(..., description="邀请码对应的角色")
    status: str = Field(..., description="邀请码状态")
    max_uses: int = Field(..., description="最大使用次数")
    used_count: int = Field(..., description="已使用次数")
    description: Optional[str] = Field(None, description="邀请码描述")
    created_by: str = Field(..., description="创建者用户名")
    create_time: datetime = Field(..., description="创建时间")
    expire_time: Optional[datetime] = Field(None, description="过期时间")

class InvitationCodeListResponse(BaseModel):
    """邀请码列表响应模型"""
    total: int = Field(..., description="总条数")
    codes: List[InvitationCodeResponse] = Field(..., description="邀请码列表")

class InvitationCodeStatusUpdateRequest(BaseModel):
    """邀请码状态更新请求模型"""
    status: str = Field(..., description="新状态", pattern="^(active|inactive)$")

class InvitationCodeValidateRequest(BaseModel):
    """邀请码验证请求模型"""
    invite_code: str = Field(..., description="邀请码")

class InvitationCodeValidateResponse(BaseModel):
    """邀请码验证响应模型"""
    valid: bool = Field(..., description="是否有效")
    role: Optional[str] = Field(None, description="邀请码对应的角色")
    message: str = Field(..., description="验证结果消息")