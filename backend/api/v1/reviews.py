"""
审稿中心相关 API 接口

包含审稿人任务、评审意见提交等功能
"""

from datetime import datetime

from api import dependencies as deps
from core.enums import DecisionType, ManuscriptStatus, UserRole, WorkflowAction
from database.dependencies import get_db_session
from database.orm.models.editorial import EditorialBoard
from database.repositories.manuscript_participant_repo import (
    ManuscriptParticipantRepository,
)
from database.repositories.manuscript_repo import ManuscriptRepository
from database.repositories.review_opinion_repo import ReviewOpinionRepository
from database.repositories.user_repo import UserRepository
from database.uow import transactional
from fastapi import APIRouter, Depends, HTTPException
from model.response import ApiResponse
from service.manuscript_service import manuscript_workflow_service
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.log import global_logger

# 具备审稿人职能的最低角色
_REVIEWER_ROLE_MIN = UserRole.REVIEWER.value


def _can_act_as_reviewer(role: str) -> bool:
    return UserRole.get_role_level(role) >= UserRole.get_role_level(_REVIEWER_ROLE_MIN)


# 管理端列表：可承担审稿的用户角色
_REVIEWER_DIRECTORY_ROLES = (
    UserRole.REVIEWER.value,
    UserRole.EA_AE.value,
    UserRole.ASSOCIATE_EDITOR.value,
    UserRole.EDITOR.value,
    UserRole.ADMIN.value,
)

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
    """分页返回当前用户作为审稿人的任务及稿件概要。"""
    if not _can_act_as_reviewer(current_user["role"]):
        raise HTTPException(status_code=403, detail="需要审稿人及以上角色")

    uid = current_user["uid"]
    part_repo = ManuscriptParticipantRepository(session)
    opinion_repo = ReviewOpinionRepository(session)

    total = await part_repo.count_by_reviewer_tasks(uid, manuscript_status=status)
    rows = await part_repo.list_by_reviewer_page(
        uid, page, page_size, manuscript_status=status
    )

    items = []
    for participant, manuscript in rows:
        review_round = manuscript.version
        submitted = await opinion_repo.exists_for_round(
            manuscript.manuscript_id, uid, review_round
        )
        items.append(
            {
                "task_id": participant.participant_id,
                "manuscript_id": manuscript.manuscript_id,
                "title": manuscript.title,
                "abstract": (manuscript.abstract or "")[:500],
                "subject": manuscript.subject,
                "stage": manuscript.stage,
                "status": manuscript.status,
                "assigned_at": participant.assigned_at.isoformat()
                if participant.assigned_at
                else None,
                "review_status": "submitted" if submitted else "pending",
                "review_round": review_round,
            }
        )

    global_logger.debug(
        "Reviews",
        f"获取审稿任务 - uid: {uid}, page: {page}, total: {total}",
    )
    return ApiResponse.paginated(
        items=items, total=total, page=page, page_size=page_size
    )


@router.put("/me/tasks/{task_id}", summary="提交评审意见")
async def submit_review_opinion(
    task_id: int,
    score: int,
    comments: str,
    recommendations: str | None = None,
    decision: str | None = None,
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    提交评审意见（1–10 分，decision 为 accept/reject/revision）。
    当本轮所有活跃审稿人均已提交时，自动将稿件推进至「评审完成」。
    """
    if not _can_act_as_reviewer(current_user["role"]):
        raise HTTPException(status_code=403, detail="需要审稿人及以上角色")

    if decision is not None and decision not in DecisionType.get_all_types():
        raise HTTPException(status_code=400, detail="无效的 decision")
    if not 1 <= score <= 10:
        raise HTTPException(status_code=400, detail="评分需在 1–10 之间")
    if not comments or not comments.strip():
        raise HTTPException(status_code=400, detail="评审意见不能为空")

    uid = current_user["uid"]
    part_repo = ManuscriptParticipantRepository(session)
    opinion_repo = ReviewOpinionRepository(session)
    m_repo = ManuscriptRepository(session)

    wf_extra = None
    all_submitted = False
    review_round = 0
    manuscript_id_out: int | None = None

    try:
        async with transactional(session):
            participant = await part_repo.get_by_id(task_id)
            if (
                not participant
                or participant.user_uid != uid
                or participant.role_type != "reviewer"
            ):
                raise ValueError("审稿任务不存在或无权操作")
            if not participant.is_active:
                raise ValueError("该审稿任务已失效")
            if participant.completed_at is not None:
                raise ValueError("该审稿任务已完成，请勿重复提交")

            manuscript = await m_repo.get_by_manuscript_id(participant.manuscript_id)
            if not manuscript:
                raise ValueError("稿件不存在")
            if manuscript.status != ManuscriptStatus.UNDER_PEER_REVIEW.value:
                raise ValueError("当前稿件状态不可提交评审意见")

            review_round = manuscript.version
            manuscript_id_out = manuscript.manuscript_id
            if await opinion_repo.exists_for_round(
                manuscript.manuscript_id, uid, review_round
            ):
                raise ValueError("本轮评审意见已提交")

            await opinion_repo.insert(
                manuscript_id=manuscript.manuscript_id,
                reviewer_uid=uid,
                stage=manuscript.stage,
                review_round=review_round,
                review_score=score,
                review_comments=comments.strip(),
                recommendations=recommendations.strip() if recommendations else None,
                decision=decision,
            )

            participant.completed_at = datetime.now()
            await session.flush()

            active_reviewers = await part_repo.list_active_reviewers_for_manuscript(
                manuscript.manuscript_id
            )
            all_submitted = True
            for r in active_reviewers:
                if not await opinion_repo.exists_for_round(
                    manuscript.manuscript_id, r.user_uid, review_round
                ):
                    all_submitted = False
                    break

            if all_submitted:
                wf_extra = await manuscript_workflow_service.execute_action(
                    manuscript_id=manuscript.manuscript_id,
                    action=WorkflowAction.REVIEW.value,
                    user_id=uid,
                    user_role=current_user["role"],
                    session=session,
                )

        global_logger.info(
            "Reviews",
            f"提交审稿意见 - task_id: {task_id}, uid: {uid}, decision: {decision}, "
            f"all_complete: {all_submitted}",
        )

        return ApiResponse.success(
            data={
                "task_id": task_id,
                "manuscript_id": manuscript_id_out,
                "review_round": review_round,
                "workflow": wf_extra,
            },
            message="评审意见提交成功",
        )
    except ValueError as e:
        global_logger.warning("Reviews", f"提交审稿意见失败 - task_id: {task_id}, {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reviewers", summary="获取审稿人列表（管理员）")
async def get_reviewer_list(
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    current_user: dict = Depends(deps.get_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    """管理员分页查询可审稿用户目录及简单统计。"""
    user_repo = UserRepository(session)
    opinion_repo = ReviewOpinionRepository(session)

    items_rows, total = await user_repo.list_reviewers_page(
        page,
        page_size,
        roles=_REVIEWER_DIRECTORY_ROLES,
        keyword=keyword,
    )
    uids = [r["uid"] for r in items_rows]
    stats = await opinion_repo.stats_for_reviewers(uids)

    # 编委信息
    board_map: dict[int, dict] = {}
    if uids:
        br = (
            (
                await session.execute(
                    select(
                        EditorialBoard.user_uid,
                        EditorialBoard.position,
                        EditorialBoard.research_areas,
                        EditorialBoard.is_active,
                    ).where(EditorialBoard.user_uid.in_(uids))
                )
            )
            .mappings()
            .all()
        )
        for row in br:
            board_map[int(row["user_uid"])] = dict(row)

    items = []
    for row in items_rows:
        uid = row["uid"]
        st = stats.get(uid, {"total_reviews": 0, "average_score": 0.0})
        b = board_map.get(uid)
        items.append(
            {
                "uid": uid,
                "username": row["username"],
                "email": row["email"],
                "role": row["role"],
                "editorial_board": b,
                "review_stats": {
                    "total_reviews": st["total_reviews"],
                    "average_score": round(st["average_score"], 2)
                    if st["average_score"]
                    else 0.0,
                },
            }
        )

    return ApiResponse.paginated(
        items=items, total=total, page=page, page_size=page_size
    )
