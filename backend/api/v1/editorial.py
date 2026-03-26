"""
编辑中心相关 API 接口

包含编委会管理、编辑看板等功能
"""
from fastapi import APIRouter, HTTPException, Depends

from core.enums import UserRole
from api import dependencies as deps
from utils.log import global_logger

from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_db_session

# 创建编辑中心路由
router = APIRouter(
    prefix="/editorial",
    tags=["编辑中心相关接口"],
    dependencies=[Depends(deps.check_db_service), Depends(deps.check_redis_service)],
    responses={
        401: {"description": "未授权"},
        403: {"description": "禁止访问"},
        404: {"description": "资源不存在"},
    },
)


@router.get("/dashboard", summary="获取编辑看板")
async def get_editorial_dashboard(
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取编辑工作台看板数据
    
    功能说明：
    1. 待处理稿件数
    2. 进行中审稿数
    3. 统计数据
    
    Args:
        current_user: 当前用户信息
        session: 数据库会话
        
    Returns:
        dict: 看板统计数据
    """
    # TODO: 实现编辑看板统计
    global_logger.debug("Editorial", f"获取编辑看板 - uid: {current_user['uid']}, role: {current_user['role']}")
    
    return {
        "pending_manuscripts": 0,
        "under_review": 0,
        "completed_reviews": 0,
        "statistics": {}
    }


@router.get("/board", summary="获取编委会列表")
async def get_editorial_board(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取编委会成员列表
    
    Args:
        page: 页码
        page_size: 每页数量
        current_user: 当前用户信息
        session: 数据库会话
        
    Returns:
        dict: 编委会成员列表
    """
    # TODO: 实现编委会查询
    return {
        "total": 0,
        "page": page,
        "page_size": page_size,
        "members": []
    }


@router.post("/board", summary="添加编委会成员（管理员）")
async def add_editorial_board_member(
    user_id: int,
    position: str,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    添加编委会成员（仅限管理员或主编）
    
    Args:
        user_id: 用户 ID
        position: 职位（editor/associate_editor/ea_ae）
        current_user: 管理员用户信息
        session: 数据库会话
        
    Returns:
        dict: 添加成功消息
    """
    # TODO: 实现编委会成员添加逻辑
    global_logger.info("Editorial", f"添加编委 - admin_uid: {current_user['uid']}, target_uid: {user_id}, position: {position}")
    
    return {"message": "编委成员添加成功"}
