"""
[DEPRECATED] 文献相关 Pydantic 模型

本模块已废弃，请使用 model/manuscript.py 代替。

废弃原因：
1. Journal 模型已统一为 Manuscript 模型
2. UploadFile 不应作为 Pydantic BaseModel 字段
   - 应在路由函数中使用 File() / UploadFile 依赖注入

迁移指南：
- JournalUploadRequest -> ManuscriptUploadRequest
- JournalUploadResponse -> ManuscriptUploadResponse
- JournalInfo -> ManuscriptInfo
- JournalListResponse -> ManuscriptListResponse
- JournalStatusUpdateRequest -> ManuscriptStatusUpdateRequest

废弃日期：2026-03-26
保留原因：向后兼容
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

from fastapi import UploadFile

# [DEPRECATED] UploadFile 不应放在 Pydantic BaseModel 中
# 请参考 model/manuscript.py 中的正确用法

class JournalUploadRequest(BaseModel):
    """文献上传请求模型"""
    title: str = Field(..., description="文献标题")
    authors: str = Field(..., description="文献作者，多个作者用逗号分隔")
    abstract: Optional[str] = Field(None, description="文献摘要")
    subject: str = Field(..., description="文献主题")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    file: UploadFile = Field(..., description="文献文件")

class JournalUploadResponse(BaseModel):
    """文献上传响应模型"""
    jid: int = Field(..., description="文献ID")
    title: str = Field(..., description="文献标题")
    status: str = Field(..., description="文献状态")
    upload_time: datetime = Field(default_factory=datetime.now, description="上传时间")

class JournalInfo(BaseModel):
    """文献信息模型"""
    jid: int = Field(..., description="文献ID")
    title: str = Field(..., description="文献标题")
    authors: str = Field(..., description="文献作者")
    abstract: Optional[str] = Field(None, description="文献摘要")
    status: str = Field(..., description="文献状态")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    upload_time: str = Field(..., description="上传时间")
    update_time: Optional[str] = Field(None, description="更新时间")

class JournalListResponse(BaseModel):
    """文献列表响应模型"""
    total: int = Field(..., description="总条数")
    journals: List[JournalInfo] = Field(..., description="文献列表")

class JournalStatusUpdateRequest(BaseModel):
    """文献状态更新请求模型"""
    status: str = Field(..., description="文献状态", pattern="^(uploading|pending|reviewing|published|rejected|deleted)$")
    comment: Optional[str] = Field(None, description="审核意见")
