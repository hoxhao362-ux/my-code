"""
编辑中心相关 API 接口

包含编委会管理、编辑看板等功能
"""

from api import dependencies as deps
from core.enums import ManuscriptStatus, ReviewStage, UserRole
from database.dependencies import get_db_session
from database.orm.models.editorial import EditorialBoard
from database.orm.models.manuscript import Manuscript
from database.repositories.editorial_board_repo import EditorialBoardRepository
from database.repositories.manuscript_repo import ManuscriptRepository
from database.repositories.user_repo import UserRepository
from database.uow import transactional
from fastapi import APIRouter, Depends, HTTPException
from model.manuscript import EditorialPendingItemDTO
from model.response import ApiResponse
from service.admin_log_service import admin_log_service
from sqlalchemy.ext.asyncio import AsyncSession
from utils.log import global_logger

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
    global_logger.debug(
        "Editorial",
        f"获取编辑看板 - uid: {current_user['uid']}, role: {current_user['role']}",
    )

    repo = ManuscriptRepository(session)

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

    # 通过 Repository 查询各状态统计
    status_counts = await repo.get_status_breakdown()

    # 计算各类别数量
    pending_count = sum(status_counts.get(s, 0) for s in pending_statuses)
    under_review_count = sum(status_counts.get(s, 0) for s in under_review_statuses)
    completed_count = sum(status_counts.get(s, 0) for s in completed_statuses)
    total_count = sum(status_counts.values())

    # 通过 Repository 查询待处理稿件 top 10
    pending_manuscripts = await repo.list_by_statuses(
        pending_statuses,
        limit=10,
        order_by=Manuscript.create_time.asc(),
    )

    # 使用 Pydantic DTO 转换为响应格式
    pending_list = [
        EditorialPendingItemDTO.model_validate(m).model_dump()
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

    return ApiResponse.success(
        data={
            "pending_manuscripts": pending_count,
            "under_review": under_review_count,
            "completed_reviews": completed_count,
            "total_manuscripts": total_count,
            "statistics": {
                "by_status": status_counts,
                "by_stage": stage_stats,
            },
            "pending_list": pending_list,
        }
    )


_BOARD_POSITIONS = frozenset({"editor", "associate_editor", "ea_ae"})
_POSITION_TO_ROLE = {
    "editor": UserRole.EDITOR.value,
    "associate_editor": UserRole.ASSOCIATE_EDITOR.value,
    "ea_ae": UserRole.EA_AE.value,
}


@router.get("/board", summary="获取编委会列表")
async def get_editorial_board(
    page: int = 1,
    page_size: int = 10,
    position: str | None = None,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """分页返回在职编委会成员（可筛选职位）。"""
    if position and position not in _BOARD_POSITIONS:
        raise HTTPException(status_code=400, detail="无效的职位筛选")

    repo = EditorialBoardRepository(session)
    total = await repo.count_board(position=position, is_active=True)
    rows = await repo.list_board_page(
        page, page_size, position=position, is_active=True
    )
    for r in rows:
        if r.get("appointed_at"):
            r["appointed_at"] = r["appointed_at"].isoformat()

    global_logger.debug(
        "Editorial",
        f"编委列表 - requester_uid: {current_user['uid']}, total: {total}",
    )
    return ApiResponse.paginated(
        items=rows, total=total, page=page, page_size=page_size
    )


@router.post("/board", summary="添加编委会成员（管理员）")
async def add_editorial_board_member(
    user_id: int,
    position: str,
    title: str | None = None,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """任命编委并提升用户角色（不低于对应职位）。"""
    if position not in _BOARD_POSITIONS:
        raise HTTPException(status_code=400, detail="position 须为 editor/associate_editor/ea_ae")

    eb_repo = EditorialBoardRepository(session)
    user_repo = UserRepository(session)

    if await eb_repo.get_by_user_uid(user_id):
        raise HTTPException(status_code=400, detail="该用户已在编委会中")

    from datetime import datetime

    try:
        board_id_val: int | None = None
        appointed_val = None
        async with transactional(session):
            user = await user_repo.get_by_id(user_id)
            if not user or user.is_deleted:
                raise HTTPException(status_code=404, detail="用户不存在")

            row = EditorialBoard(
                user_uid=user_id,
                position=position,
                title=title,
                research_areas=None,
                appointed_at=datetime.now(),
                appointed_by_uid=current_user["uid"],
                is_active=True,
            )
            session.add(row)
            await session.flush()
            board_id_val = row.board_id
            appointed_val = row.appointed_at

            target_role = _POSITION_TO_ROLE[position]
            if UserRole.get_role_level(user.role) < UserRole.get_role_level(
                target_role
            ):
                user.role = target_role
                global_logger.info(
                    "Editorial",
                    f"编委任命同步提升角色 uid={user_id} -> {target_role}",
                )

        await admin_log_service.record_admin_log(
            admin_uid=current_user["uid"],
            admin_username=current_user.get("username", str(current_user["uid"])),
            operation_type="添加编委会成员",
            operation_object=f"user_uid={user_id}",
            operation_details=f"position={position}, board_id={board_id_val}",
            session=session,
        )

        global_logger.info(
            "Editorial",
            f"添加编委 - admin_uid: {current_user['uid']}, target_uid: {user_id}, position: {position}",
        )
        return ApiResponse.success(
            data={
                "board_id": board_id_val,
                "user_uid": user_id,
                "position": position,
                "appointed_at": appointed_val.isoformat() if appointed_val else None,
            },
            message="编委成员添加成功",
        )
    except HTTPException:
        raise
    except Exception as e:
        global_logger.exception("Editorial", f"添加编委失败: {e}")
        raise HTTPException(status_code=500, detail="添加编委失败") from e
