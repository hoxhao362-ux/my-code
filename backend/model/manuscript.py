"""
稿件相关 Pydantic 模型（DTO）

本模块包含稿件相关的请求/响应数据传输对象。
替代已废弃的 model/journal.py。

注意：UploadFile 不应作为 Pydantic BaseModel 的字段，
应作为 FastAPI 路由参数使用 File() / UploadFile 依赖注入方式。

创建日期：2026-03-26
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class ManuscriptUploadRequest(BaseModel):
    """
    稿件上传请求模型
    
    注意：文件上传字段 (file: UploadFile) 不包含在此模型中，
    应在路由函数中单独声明为 FastAPI 依赖：
    
    Example:
        @router.post("/upload")
        async def upload_manuscript(
            request: ManuscriptUploadRequest,
            file: UploadFile = File(...),
        ):
            pass
    """
    title: str = Field(..., description="稿件标题", min_length=1, max_length=500)
    authors: str = Field(..., description="作者列表，多个作者用逗号分隔")
    abstract: Optional[str] = Field(None, description="稿件摘要", max_length=5000)
    subject: str = Field(..., description="学科/主题分类")
    keywords: Optional[str] = Field(None, description="关键词，多个用逗号分隔")


class ManuscriptUploadResponse(BaseModel):
    """稿件上传响应模型"""
    manuscript_id: int = Field(..., description="稿件ID")
    title: str = Field(..., description="稿件标题")
    status: str = Field(..., description="稿件状态")
    upload_time: datetime = Field(default_factory=datetime.now, description="上传时间")
    message: str = Field(default="上传成功", description="响应消息")


class ManuscriptInfo(BaseModel):
    """
    稿件信息模型
    
    用于展示稿件详情和列表项
    """
    manuscript_id: int = Field(..., description="稿件ID", alias="id")
    title: str = Field(..., description="稿件标题")
    authors: str = Field(..., description="作者列表")
    abstract: Optional[str] = Field(None, description="稿件摘要")
    status: str = Field(..., description="稿件状态")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小（字节）")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    
    class Config:
        populate_by_name = True


class ManuscriptListResponse(BaseModel):
    """稿件列表响应模型"""
    total: int = Field(..., description="总条数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页条数")
    manuscripts: List[ManuscriptInfo] = Field(default_factory=list, description="稿件列表")


class ManuscriptStatusUpdateRequest(BaseModel):
    """稿件状态更新请求模型"""
    status: str = Field(..., description="新状态值")
    comment: Optional[str] = Field(None, description="状态变更备注/审核意见")
    reason: Optional[str] = Field(None, description="变更原因（如拒稿原因）")


class ManuscriptDeleteRequest(BaseModel):
    """稿件删除请求模型（软删除）"""
    reason: Optional[str] = Field(None, description="删除原因", max_length=500)


# ========== 兼容旧版 Journal 模型的别名 ==========
# 以下别名用于向后兼容，建议逐步迁移到新的 Manuscript 命名

JournalUploadRequest = ManuscriptUploadRequest
JournalUploadResponse = ManuscriptUploadResponse
JournalInfo = ManuscriptInfo
JournalListResponse = ManuscriptListResponse
JournalStatusUpdateRequest = ManuscriptStatusUpdateRequest
