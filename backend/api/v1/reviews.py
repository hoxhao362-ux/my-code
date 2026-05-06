"""
审稿中心相关 API 接口

包含审稿人任务、评审意见提交等功能
"""

<<<<<<< HEAD
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

=======
from api import dependencies as deps
from database.dependencies import get_db_session
from fastapi import APIRouter, Depends
from model.response import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession
from utils.log import global_logger

# 创建审稿中心路由
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
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
<<<<<<< HEAD
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

=======
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
    """
    TODO: 实现审稿任务查询

    建议实现流程：
    1. 通过 current_user['uid'] 查询 ManuscriptParticipant 表，筛选 role_type='reviewer' 且 is_active=True 的记录
    2. 联表 Manuscript 表获取稿件标题、状态、阶段等信息
    3. 如有 status 参数，进一步筛选稿件状态（如 under_peer_review/review_completed 等）
    4. 计算总数 total，执行分页查询
    5. 额外查询每条任务关联的 ReviewOpinion，判断该审稿人是否已提交意见（用于前端显示"待审/已审"状态）
    6. 组装响应数据，返回分页结果

    所需 ORM 模型：
    - ManuscriptParticipant (database/orm/models/manuscript.py) — 稿件参与者表，核心查询对象，含 participant_id/manuscript_id/user_uid/role_type/assigned_at/is_active/completed_at
    - Manuscript (database/orm/models/manuscript.py) — 稿件主表，联表获取标题/状态/阶段
    - ReviewOpinion (database/orm/models/review_opinion.py) — 审稿意见表，判断是否已提交意见

    建议 Repository 方法：
    - ManuscriptParticipantRepository.list_by_reviewer(reviewer_uid, page, page_size, status=None) — 分页查询某审稿人的活跃任务
    - ManuscriptParticipantRepository.count_by_reviewer(reviewer_uid, status=None) — 统计任务数
    - ReviewOpinionRepository.get_by_reviewer_and_manuscript(reviewer_uid, manuscript_id) — 查询某审稿人对某稿件的意见

    建议 Service 调用链：
    API → ManuscriptParticipantRepository.list_by_reviewer(uid) → 联表 Manuscript
        → 逐条查询 ReviewOpinion 是否已提交 → 组装任务状态 → 返回分页

    权限要求：
    - 当前使用 get_current_active_user（已登录用户均可访问）
    - 需要验证当前用户角色为 reviewer 及以上，建议增加 require_role(reviewer) 依赖

    返回数据格式建议：
    {
        "items": [
            {
                "task_id": 1,  // participant_id
                "manuscript_id": 10001,
                "title": "基于深度学习的图像识别研究",
                "authors": "张三,李四",
                "subject": "计算机科学",
                "stage": "peer_review",
                "status": "under_peer_review",
                "assigned_at": "2026-04-01T10:00:00",
                "review_status": "pending",  // pending=待审 / submitted=已审
                "deadline": "2026-05-01T23:59:59"  // 如有截止时间字段
            }
        ],
        "total": 3,
        "page": 1,
        "page_size": 10
    }

    注意事项：
    - 审稿任务实质是 ManuscriptParticipant 中 role_type='reviewer' 的记录，task_id 即 participant_id
    - 需区分"待审"（is_active=True 且 completed_at 为空）和"已完成"（completed_at 有值）的任务
    - status 参数语义为稿件状态筛选，非任务状态，需在文档中明确说明
    - 查询 ReviewOpinion 时注意审稿轮次 review_round，同一审稿人可能有多轮意见
    - 联表查询建议使用 joinedload 预加载 Manuscript 避免懒加载 N+1 问题
    """
    global_logger.debug(
        "Reviews", f"获取审稿任务 - uid: {current_user['uid']}, page: {page}"
    )

    return ApiResponse.paginated(items=[], total=0, page=page, page_size=page_size)

>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea

@router.put("/me/tasks/{task_id}", summary="提交评审意见")
async def submit_review_opinion(
    task_id: int,
    score: int,
    comments: str,
    recommendations: str | None = None,
<<<<<<< HEAD
    decision: str | None = None,
=======
    decision: str = None,
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
    current_user: dict = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
<<<<<<< HEAD
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
=======
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
    """
    TODO: 实现评审意见提交逻辑

    建议实现流程：
    1. 根据 task_id 查询 ManuscriptParticipant 记录，验证该任务确实属于当前用户（user_uid 匹配）
    2. 验证任务状态：is_active 必须为 True，completed_at 必须为空（未完成才能提交）
    3. 查询对应 Manuscript 记录，确认稿件状态允许提交意见（如 under_peer_review）
    4. 创建 ReviewOpinion 记录，填充 manuscript_id/reviewer_uid/stage/review_round/review_score/review_comments/recommendations/decision/submitted_at
    5. 更新 ManuscriptParticipant 的 completed_at 为当前时间
    6. 检查该稿件所有分配的审稿人是否都已完成评审，如果是则触发稿件状态流转（review_completed）
    7. 在事务中执行上述所有操作
    8. 通过消息通知服务（如有）通知编辑有新评审意见

    所需 ORM 模型：
    - ManuscriptParticipant (database/orm/models/manuscript.py) — 确认审稿任务归属，更新 completed_at
    - ReviewOpinion (database/orm/models/review_opinion.py) — 核心写入对象，创建评审意见记录
    - Manuscript (database/orm/models/manuscript.py) — 查询稿件状态，可能触发状态流转

    建议 Repository 方法：
    - ManuscriptParticipantRepository.get_by_id(participant_id) — 查询审稿任务详情
    - ReviewOpinionRepository.add(opinion) — 新增评审意见
    - ReviewOpinionRepository.count_by_manuscript(manuscript_id, review_round) — 统计某稿件某轮已提交意见数
    - ManuscriptParticipantRepository.count_active_reviewers(manuscript_id) — 统计某稿件活跃审稿人数

    建议 Service 调用链：
    API → 校验 task 归属 → ManuscriptParticipantRepository.get_by_id()
        → 验证稿件状态 → 创建 ReviewOpinion → ReviewOpinionRepository.add()
        → 更新 ManuscriptParticipant.completed_at
        → 检查是否全部审完 → manuscript_workflow_service.execute_action(review)
        → 返回成功

    权限要求：
    - 当前使用 get_current_active_user（已登录用户均可访问）
    - 必须验证 task_id 归属当前用户，防止越权提交他人审稿意见
    - 建议增加 require_role(reviewer) 依赖

    返回数据格式建议：
    {
        "opinion_id": 1,
        "manuscript_id": 10001,
        "review_score": 8,
        "decision": "accept",
        "submitted_at": "2026-04-18T14:30:00"
    }

    注意事项：
    - ReviewOpinion.stage 应从 Manuscript.stage 获取，与稿件当前阶段一致
    - ReviewOpinion.review_round 需根据该稿件已有的最大轮次 +1 或沿用当前轮次（建议从 Manuscript.version 推导）
    - decision 值应为 accept/reject/revision 之一，建议使用 DecisionType 枚举校验
    - review_score 评分范围需约定（如 1-10），建议在接口层增加范围校验
    - 同一审稿人对同一稿件同一轮次不应重复提交，需检查是否已有 ReviewOpinion 记录
    - 全部审稿人完成后触发状态流转是核心业务逻辑，需确保原子性
    """
    global_logger.info(
        "Reviews",
        f"提交评审意见 - task_id: {task_id}, uid: {current_user['uid']}, decision: {decision}",
    )

    return ApiResponse.success(message="评审意见提交成功")
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea


@router.get("/reviewers", summary="获取审稿人列表（管理员）")
async def get_reviewer_list(
    page: int = 1,
    page_size: int = 10,
<<<<<<< HEAD
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
=======
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
    """
    TODO: 实现审稿人列表查询

    建议实现流程：
    1. 查询 User 表中 role='reviewer' 或更高角色（editor/associate_editor 也可审稿）的用户
    2. 联表 EditorialBoard 获取编委信息（职位、研究领域），审稿人可能是编委成员
    3. 联表统计每个审稿人的历史审稿数据：已完成评审数、平均评分等（通过 ReviewOpinion 聚合）
    4. 支持分页查询，计算总数
    5. 返回包含审稿人基本信息和统计数据的分页列表

    所需 ORM 模型：
    - User (database/orm/models/user.py) — 核心查询对象，筛选 role 为 reviewer 及以上
    - EditorialBoard (database/orm/models/editorial.py) — 联表获取编委职位和研究领域
    - ReviewOpinion (database/orm/models/review_opinion.py) — 聚合统计审稿人的历史评审数据

    建议 Repository 方法：
    - UserRepository.list_reviewers(page, page_size) — 分页查询审稿人角色用户
    - UserRepository.count_reviewers() — 统计审稿人总数
    - ReviewOpinionRepository.stats_by_reviewer(reviewer_uid) — 统计某审稿人的评审次数/平均分

    建议 Service 调用链：
    API → UserRepository.list_reviewers() → 联表 EditorialBoard
        → 批量查询 ReviewOpinion 统计 → 组装数据 → 返回分页

    权限要求：
    - 当前使用 get_admin_user（仅管理员可访问），符合要求
    - 此接口用于管理员分配审稿人时查看可用的审稿人列表，权限合理

    返回数据格式建议：
    {
        "items": [
            {
                "uid": 5,
                "username": "reviewer_zhang",
                "email": "zhang@example.com",
                "role": "reviewer",
                "is_active_board_member": true,  // 是否是编委
                "position": "associate_editor",  // 编委职位（如有）
                "research_areas": "人工智能,自然语言处理",  // 研究领域
                "review_stats": {
                    "total_reviews": 12,
                    "average_score": 7.5
                }
            }
        ],
        "total": 8,
        "page": 1,
        "page_size": 10
    }

    注意事项：
    - 审稿人不仅限于 role='reviewer'，editor/associate_editor/ea_ae 也可能参与审稿
    - 建议增加 subject/keyword 筛选参数，方便管理员按研究领域查找审稿人
    - 批量查询统计数据时注意性能，避免 N+1 问题，建议使用子查询或批量聚合
    - 审稿人的历史统计数据可考虑缓存到 Redis，定期刷新
    - 需排除 is_deleted=True 的用户
    """
    return ApiResponse.paginated(items=[], total=0, page=page, page_size=page_size)
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea
