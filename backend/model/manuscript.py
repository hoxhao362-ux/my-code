"""
稿件相关 Pydantic 模型（DTO）

本模块包含稿件相关的请求/响应数据传输对象。
替代已废弃的 model/journal.py。

注意：UploadFile 不应作为 Pydantic BaseModel 的字段，
应作为 FastAPI 路由参数使用 File() / UploadFile 依赖注入方式。

创建日期：2026-03-26
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


# ============================================================
# 请求模型
# ============================================================

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


class ManuscriptStatusUpdateRequest(BaseModel):
    """稿件状态更新请求模型"""
    status: str = Field(..., description="新状态值")
    comment: Optional[str] = Field(None, description="状态变更备注/审核意见")
    reason: Optional[str] = Field(None, description="变更原因（如拒稿原因）")


class ManuscriptDeleteRequest(BaseModel):
    """稿件删除请求模型（软删除）"""
    reason: Optional[str] = Field(None, description="删除原因", max_length=500)


# ============================================================
# 响应模型
# ============================================================

class ManuscriptUploadResponse(BaseModel):
    """稿件上传响应模型"""
    manuscript_id: int = Field(..., description="稿件ID")
    title: str = Field(..., description="稿件标题")
    status: str = Field(..., description="稿件状态")
    upload_time: str = Field(..., description="上传时间")
    message: str = Field(default="上传成功", description="响应消息")


class ManuscriptListItemDTO(BaseModel):
    """
    稿件列表项 DTO
    
    用于稿件列表展示，从 Manuscript ORM 对象转换。
    使用 from_attributes=True 支持 model_validate(orm_object)。
    """
    model_config = ConfigDict(from_attributes=True)

    manuscript_id: int = Field(..., description="稿件ID")
    title: str = Field(..., description="稿件标题")
    authors: str = Field(..., description="作者列表")
    subject: str = Field(default="", description="学科/主题")
    stage: str = Field(default="", description="流转阶段")
    status: str = Field(..., description="稿件状态")
    version: int = Field(default=1, description="版本号")
    create_time: Optional[str] = Field(None, description="创建时间")
    update_time: Optional[str] = Field(None, description="更新时间")


class ManuscriptDetailDTO(BaseModel):
    """
    稿件详情 DTO
    
    用于稿件详情页展示，从 Manuscript ORM 对象转换。
    使用 from_attributes=True 支持 model_validate(orm_object)。
    """
    model_config = ConfigDict(from_attributes=True)

    manuscript_id: int = Field(..., description="稿件ID")
    author_uid: int = Field(..., description="作者用户ID")
    title: str = Field(..., description="稿件标题")
    article_type: str = Field(default="Research Article", description="文章类型")
    section_category: Optional[str] = Field(None, description="栏目/类别")
    keywords: str = Field(default="", description="关键字")
    first_author: str = Field(default="", description="第一作者")
    corresponding_author: str = Field(default="", description="通讯作者")
    order_of_authors: str = Field(default="[]", description="作者排序")
    authors: str = Field(..., description="作者列表")
    abstract: Optional[str] = Field(None, description="摘要")
    subject: str = Field(..., description="学科/主题")
    stage: str = Field(..., description="流转阶段")
    status: str = Field(..., description="稿件状态")
    version: int = Field(default=1, description="版本号")
    file_hash: Optional[str] = Field(None, description="文件哈希")
    file_bucket: Optional[str] = Field(None, description="文件存储桶路径")
    file_name: Optional[str] = Field(None, description="原始文件名")
    file_size: Optional[int] = Field(None, description="文件大小（字节）")
    create_time: Optional[str] = Field(None, description="创建时间")
    update_time: Optional[str] = Field(None, description="更新时间")


class EditorialPendingItemDTO(BaseModel):
    """
    编辑看板待处理稿件项 DTO
    
    用于编辑看板中待处理稿件列表展示。
    """
    model_config = ConfigDict(from_attributes=True)

    manuscript_id: int = Field(..., description="稿件ID")
    title: str = Field(..., description="稿件标题")
    authors: str = Field(..., description="作者列表")
    status: str = Field(..., description="稿件状态")
    stage: str = Field(..., description="流转阶段")
    create_time: Optional[str] = Field(None, description="创建时间")
    update_time: Optional[str] = Field(None, description="更新时间")


class ArticleListItemDTO(BaseModel):
    """
    公开文章列表项 DTO
    
    用于公共接口中已发表论文列表展示。
    字段命名以 article_ 前缀对齐公共接口语义。
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    article_id: int = Field(..., alias="manuscript_id", description="文章ID")
    title: str = Field(..., description="文章标题")
    authors: str = Field(..., description="作者列表")
    abstract: Optional[str] = Field(None, description="摘要")
    subject: Optional[str] = Field(None, description="学科/主题")
    publish_time: Optional[str] = Field(None, alias="update_time", description="发表时间")


class ArticleDetailDTO(BaseModel):
    """
    公开文章详情 DTO
    
    用于公共接口中已发表论文详情展示。
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    article_id: int = Field(..., alias="manuscript_id", description="文章ID")
    title: str = Field(..., description="文章标题")
    authors: str = Field(..., description="作者列表")
    abstract: Optional[str] = Field(None, description="摘要")
    subject: str = Field(..., description="学科/主题")
    version: Optional[int] = Field(None, description="版本号")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小")
    publish_time: Optional[str] = Field(None, alias="update_time", description="发表时间")
    create_time: Optional[str] = Field(None, description="创建时间")


# ============================================================
# 兼容旧版模型
# ============================================================

class ManuscriptInfo(BaseModel):
    """
    稿件信息模型（兼容旧版）
    
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


# ========== 兼容旧版 Journal 模型的别名 ==========
JournalUploadRequest = ManuscriptUploadRequest
JournalUploadResponse = ManuscriptUploadResponse
JournalInfo = ManuscriptInfo
JournalListResponse = ManuscriptListResponse
JournalStatusUpdateRequest = ManuscriptStatusUpdateRequest
