"""
编辑中心相关 API 接口

包含编委会管理、编辑看板等功能
"""
from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import UserRole, ManuscriptStatus, ReviewStage
from model.response import ApiResponse
from api import dependencies as deps
from utils.log import global_logger

from database.dependencies import get_db_session
from database.orm.models.manuscript import Manuscript

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
    global_logger.debug("Editorial", f"获取编辑看板 - uid: {current_user['uid']}, role: {current_user['role']}")
    
    # 定义待处理状态（需要编辑从业者处理的状态）
    pending_statuses = [
        ManuscriptStatus.PENDING_INITIAL_REVIEW.value,
        ManuscriptStatus.REVISION_SUBMITTED.value,
        ManuscriptStatus.PENDING_PEER_REVIEW.value,
        ManuscriptStatus.REVIEW_COMPLETED.value,
        ManuscriptStatus.PENDING_FINAL_DECISION.value,
    ]
    
    # 定义审稿中状态
    under_review_statuses = [
        ManuscriptStatus.UNDER_INITIAL_REVIEW.value,
        ManuscriptStatus.UNDER_PEER_REVIEW.value,
        ManuscriptStatus.UNDER_FINAL_DECISION.value,
    ]
    
    # 定义已完成状态
    completed_statuses = [
        ManuscriptStatus.PUBLISHED.value,
        ManuscriptStatus.FINAL_DECISION_REJECTED.value,
        ManuscriptStatus.WITHDRAWN.value,
        ManuscriptStatus.TRANSFERRED.value,
    ]
    
    # 查询各状态统计
    status_stats_query = (
        select(Manuscript.status, func.count())
        .where(Manuscript.is_deleted == False)
        .group_by(Manuscript.status)
    )
    status_result = await session.execute(status_stats_query)
    status_counts = {row[0]: row[1] for row in status_result.fetchall()}
    
    # 计算各类别数量
    pending_count = sum(status_counts.get(s, 0) for s in pending_statuses)
    under_review_count = sum(status_counts.get(s, 0) for s in under_review_statuses)
    completed_count = sum(status_counts.get(s, 0) for s in completed_statuses)
    total_count = sum(status_counts.values())
    
    # 查询待处理稿件 top 10
    pending_manuscripts_query = (
        select(Manuscript)
        .where(
            Manuscript.is_deleted == False,
            Manuscript.status.in_(pending_statuses)
        )
        .order_by(Manuscript.create_time.asc())  # 按创建时间升序，优先处理早提交的
        .limit(10)
    )
    pending_result = await session.execute(pending_manuscripts_query)
    pending_manuscripts = pending_result.scalars().all()
    
    # 转换为响应格式
    pending_list = [
        {
            "manuscript_id": m.manuscript_id,
            "title": m.title,
            "authors": m.authors,
            "status": m.status,
            "stage": m.stage,
            "create_time": m.create_time,
            "update_time": m.update_time,
        }
        for m in pending_manuscripts
    ]
    
    # 按阶段统计
    stage_stats = {
        ReviewStage.INITIAL_REVIEW.value: sum(
            status_counts.get(s, 0) 
            for s in ManuscriptStatus.get_status_by_phase(ReviewStage.INITIAL_REVIEW)
        ),
        ReviewStage.PEER_REVIEW.value: sum(
            status_counts.get(s, 0) 
            for s in ManuscriptStatus.get_status_by_phase(ReviewStage.PEER_REVIEW)
        ),
        ReviewStage.FINAL_DECISION.value: sum(
            status_counts.get(s, 0) 
            for s in ManuscriptStatus.get_status_by_phase(ReviewStage.FINAL_DECISION)
        ),
    }
    
    return ApiResponse.success(data={
        "pending_manuscripts": pending_count,
        "under_review": under_review_count,
        "completed_reviews": completed_count,
        "total_manuscripts": total_count,
        "statistics": {
            "by_status": status_counts,
            "by_stage": stage_stats,
        },
        "pending_list": pending_list,
    })


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
    return ApiResponse.paginated(
        items=[],
        total=0,
        page=page,
        page_size=page_size
    )


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
    
    return ApiResponse.success(message="编委成员添加成功")
