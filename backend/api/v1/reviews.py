"""
审稿中心相关 API 接口

包含审稿人任务、评审意见提交等功能
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from core.enums import UserRole
from api import dependencies as deps
from utils.log import global_logger

from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_db_session

# 创建审稿中心路由
router = APIRouter(
    prefix="/reviews",
    tags=["审稿中心相关接口"],
    dependencies=[Depends(deps.check_db_service), Depends(deps.check_redis_service)],
    responses={
        401: {"description": "未授权"},
        403: {"description": "禁止访问"},
        404: {"description": "资源不存在"},
    },
)


@router.get("/me/tasks", summary="获取我的审稿任务")
async def get_my_review_tasks(
    page: int = 1,
    page_size: int = 10,
    status: str | None = None,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取当前审稿人的审稿任务列表
    
    Args:
        page: 页码
        page_size: 每页数量
        status: 任务状态筛选
        current_user: 当前用户信息
        session: 数据库会话
        
    Returns:
        dict: 审稿任务列表
    """
    # TODO: 实现审稿任务查询
    global_logger.debug("Reviews", f"获取审稿任务 - uid: {current_user['uid']}, page: {page}")
    
    return {
        "total": 0,
        "page": page,
        "page_size": page_size,
        "tasks": []
    }


@router.put("/me/tasks/{task_id}", summary="提交评审意见")
async def submit_review_opinion(
    task_id: int,
    score: int,
    comments: str,
    recommendations: str | None = None,
    decision: str = None,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    提交审稿意见
    
    Args:
        task_id: 审稿任务 ID
        score: 评分
        comments: 评审意见
        recommendations: 建议
        decision: 评审结论（accept/reject/revision）
        current_user: 当前用户信息
        session: 数据库会话
        
    Returns:
        dict: 提交成功消息
    """
    # TODO: 实现评审意见提交逻辑
    global_logger.info("Reviews", f"提交评审意见 - task_id: {task_id}, uid: {current_user['uid']}, decision: {decision}")
    
    return {"message": "评审意见提交成功"}


@router.get("/reviewers", summary="获取审稿人列表（管理员）")
async def get_reviewer_list(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取所有审稿人列表（仅限管理员）
    
    Args:
        page: 页码
        page_size: 每页数量
        current_user: 管理员用户信息
        session: 数据库会话
        
    Returns:
        dict: 审稿人列表
    """
    # TODO: 实现审稿人列表查询
    return {
        "total": 0,
        "page": page,
        "page_size": page_size,
        "reviewers": []
    }
