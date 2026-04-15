"""稿件工作流状态机服务

根据枚举定义实现完整的稿件流转状态机，包含：
1. 状态转换矩阵：定义合法的状态转换路径
2. 动作权限矩阵：定义每个动作允许的用户角色
3. ManuscriptWorkflowService：执行状态转换的服务类
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import ManuscriptStatus, WorkflowAction, UserRole, DecisionType, ReviewStage
from database.orm.models.manuscript import Manuscript
from database.uow import transactional

# ============================================================
# 状态转换矩阵
# 格式: {(当前状态, 动作, 决策类型): 目标状态}
# 决策类型为 None 时表示该动作不需要决策类型
# ============================================================
TRANSITION_MAP: dict[tuple[str, str, Optional[str]], str] = {
    # ========== 初审阶段 ==========
    # 待初审 → 初审
    (ManuscriptStatus.PENDING_INITIAL_REVIEW.value, WorkflowAction.SCREEN.value, None): ManuscriptStatus.UNDER_INITIAL_REVIEW.value,
    
    # 初审中 → 决策
    (ManuscriptStatus.UNDER_INITIAL_REVIEW.value, WorkflowAction.DECIDE.value, DecisionType.ACCEPT.value): ManuscriptStatus.INITIAL_REVIEW_PASSED.value,
    (ManuscriptStatus.UNDER_INITIAL_REVIEW.value, WorkflowAction.DECIDE.value, DecisionType.REVISION.value): ManuscriptStatus.INITIAL_REVIEW_REVISION.value,
    (ManuscriptStatus.UNDER_INITIAL_REVIEW.value, WorkflowAction.DECIDE.value, DecisionType.REJECT.value): ManuscriptStatus.INITIAL_REVIEW_REJECTED.value,
    (ManuscriptStatus.UNDER_INITIAL_REVIEW.value, WorkflowAction.DECIDE.value, DecisionType.TRANSFER.value): ManuscriptStatus.TRANSFER_SUGGESTED.value,
    
    # 初审退回修改 → 作者修改后重新提交
    (ManuscriptStatus.INITIAL_REVIEW_REVISION.value, WorkflowAction.REVISE.value, None): ManuscriptStatus.PENDING_INITIAL_REVIEW.value,
    
    # 初审通过 → 进入同行评审阶段
    (ManuscriptStatus.INITIAL_REVIEW_PASSED.value, WorkflowAction.ASSIGN.value, None): ManuscriptStatus.PENDING_PEER_REVIEW.value,
    
    # ========== 同行评审阶段 ==========
    # 待同行评审 → 分配审稿人
    (ManuscriptStatus.PENDING_PEER_REVIEW.value, WorkflowAction.ASSIGN.value, None): ManuscriptStatus.UNDER_PEER_REVIEW.value,
    
    # 评审中 → 审稿人提交评审意见
    (ManuscriptStatus.UNDER_PEER_REVIEW.value, WorkflowAction.REVIEW.value, None): ManuscriptStatus.REVIEW_COMPLETED.value,
    
    # 评审完成 → 编辑决策
    (ManuscriptStatus.REVIEW_COMPLETED.value, WorkflowAction.DECIDE.value, DecisionType.ACCEPT.value): ManuscriptStatus.PENDING_FINAL_DECISION.value,
    (ManuscriptStatus.REVIEW_COMPLETED.value, WorkflowAction.DECIDE.value, DecisionType.REVISION.value): ManuscriptStatus.REVISION_REQUIRED.value,
    (ManuscriptStatus.REVIEW_COMPLETED.value, WorkflowAction.DECIDE.value, DecisionType.REJECT.value): ManuscriptStatus.FINAL_DECISION_REJECTED.value,
    (ManuscriptStatus.REVIEW_COMPLETED.value, WorkflowAction.DECIDE.value, DecisionType.TRANSFER.value): ManuscriptStatus.TRANSFER_SUGGESTED.value,
    
    # 需要修稿 → 作者修改
    (ManuscriptStatus.REVISION_REQUIRED.value, WorkflowAction.REVISE.value, None): ManuscriptStatus.REVISION_SUBMITTED.value,
    
    # 修订稿已提交 → 重新筛选
    (ManuscriptStatus.REVISION_SUBMITTED.value, WorkflowAction.SCREEN.value, None): ManuscriptStatus.PENDING_PEER_REVIEW.value,
    
    # ========== 终审阶段 ==========
    # 待终审 → 开始终审
    (ManuscriptStatus.PENDING_FINAL_DECISION.value, WorkflowAction.SCREEN.value, None): ManuscriptStatus.UNDER_FINAL_DECISION.value,
    
    # 终审中 → 最终决策
    (ManuscriptStatus.UNDER_FINAL_DECISION.value, WorkflowAction.DECIDE.value, DecisionType.ACCEPT.value): ManuscriptStatus.FINAL_DECISION_ACCEPTED.value,
    (ManuscriptStatus.UNDER_FINAL_DECISION.value, WorkflowAction.DECIDE.value, DecisionType.REVISION.value): ManuscriptStatus.FINAL_DECISION_REVISION.value,
    (ManuscriptStatus.UNDER_FINAL_DECISION.value, WorkflowAction.DECIDE.value, DecisionType.REJECT.value): ManuscriptStatus.FINAL_DECISION_REJECTED.value,
    (ManuscriptStatus.UNDER_FINAL_DECISION.value, WorkflowAction.DECIDE.value, DecisionType.TRANSFER.value): ManuscriptStatus.TRANSFER_SUGGESTED.value,
    
    # 终审修改后录用 → 作者修改后重新提交
    (ManuscriptStatus.FINAL_DECISION_REVISION.value, WorkflowAction.REVISE.value, None): ManuscriptStatus.PENDING_FINAL_DECISION.value,
    
    # ========== 录用出版阶段 ==========
    # 终审通过 → 录用确认
    (ManuscriptStatus.FINAL_DECISION_ACCEPTED.value, WorkflowAction.APPROVE.value, None): ManuscriptStatus.PENDING_ACCEPTANCE_CONFIRMATION.value,
    
    # 待录用确认 → 版权协议
    (ManuscriptStatus.PENDING_ACCEPTANCE_CONFIRMATION.value, WorkflowAction.APPROVE.value, None): ManuscriptStatus.PENDING_COPYRIGHT.value,
    
    # 待版权协议 → 校样确认
    (ManuscriptStatus.PENDING_COPYRIGHT.value, WorkflowAction.APPROVE.value, None): ManuscriptStatus.PENDING_PROOF.value,
    
    # 待校样确认 → 待出版
    (ManuscriptStatus.PENDING_PROOF.value, WorkflowAction.APPROVE.value, None): ManuscriptStatus.PENDING_PUBLICATION.value,
    
    # 待出版 → 已出版
    (ManuscriptStatus.PENDING_PUBLICATION.value, WorkflowAction.PUBLISH.value, None): ManuscriptStatus.PUBLISHED.value,
    
    # ========== 其他转换 ==========
    # 建议转投 → 已转投
    (ManuscriptStatus.TRANSFER_SUGGESTED.value, WorkflowAction.APPROVE.value, None): ManuscriptStatus.TRANSFERRED.value,
}

# 可撤稿的状态（非终态）
WITHDRAWABLE_STATUSES = [
    ManuscriptStatus.PENDING_INITIAL_REVIEW.value,
    ManuscriptStatus.UNDER_INITIAL_REVIEW.value,
    ManuscriptStatus.INITIAL_REVIEW_PASSED.value,
    ManuscriptStatus.INITIAL_REVIEW_REVISION.value,
    ManuscriptStatus.PENDING_PEER_REVIEW.value,
    ManuscriptStatus.UNDER_PEER_REVIEW.value,
    ManuscriptStatus.REVIEW_COMPLETED.value,
    ManuscriptStatus.REVISION_REQUIRED.value,
    ManuscriptStatus.REVISION_SUBMITTED.value,
    ManuscriptStatus.PENDING_FINAL_DECISION.value,
    ManuscriptStatus.UNDER_FINAL_DECISION.value,
    ManuscriptStatus.FINAL_DECISION_REVISION.value,
    ManuscriptStatus.TRANSFER_SUGGESTED.value,
]

# ============================================================
# 动作权限矩阵
# 格式: {动作: [允许的角色列表]}
# ============================================================
ACTION_PERMISSIONS: dict[str, list[str]] = {
    # 保存草稿 - 作者
    WorkflowAction.SAVE.value: [
        UserRole.AUTHOR.value,
        UserRole.USER.value,
    ],
    
    # 提交稿件 - 作者
    WorkflowAction.SUBMIT.value: [
        UserRole.AUTHOR.value,
        UserRole.USER.value,
    ],
    
    # 撤稿 - 作者可以撤回自己的稿件
    WorkflowAction.WITHDRAW.value: [
        UserRole.AUTHOR.value,
        UserRole.USER.value,
        UserRole.ADMIN.value,
    ],
    
    # 初审筛选 - 编辑部
    WorkflowAction.SCREEN.value: [
        UserRole.ADMIN.value,
        UserRole.EDITOR.value,
        UserRole.ASSOCIATE_EDITOR.value,
        UserRole.EA_AE.value,
    ],
    
    # 分配审稿人 - 编辑部
    WorkflowAction.ASSIGN.value: [
        UserRole.ADMIN.value,
        UserRole.EDITOR.value,
        UserRole.ASSOCIATE_EDITOR.value,
    ],
    
    # 提交评审意见 - 审稿人
    WorkflowAction.REVIEW.value: [
        UserRole.REVIEWER.value,
        UserRole.ADMIN.value,
        UserRole.EDITOR.value,
    ],
    
    # 编辑决策 - 编辑
    WorkflowAction.DECIDE.value: [
        UserRole.ADMIN.value,
        UserRole.EDITOR.value,
        UserRole.ASSOCIATE_EDITOR.value,
    ],
    
    # 作者修改 - 作者
    WorkflowAction.REVISE.value: [
        UserRole.AUTHOR.value,
        UserRole.USER.value,
    ],
    
    # 录用确认 - 编辑部
    WorkflowAction.APPROVE.value: [
        UserRole.ADMIN.value,
        UserRole.EDITOR.value,
        UserRole.EA_AE.value,
    ],
    
    # 出版 - 编辑部
    WorkflowAction.PUBLISH.value: [
        UserRole.ADMIN.value,
        UserRole.EDITOR.value,
    ],
}


class ManuscriptWorkflowService:
    """稿件工作流服务
    
    提供状态转换验证和执行功能
    """
    
    @staticmethod
    def get_allowed_actions(current_status: str, user_role: str) -> list[str]:
        """根据当前状态和用户角色返回允许的动作
        
        Args:
            current_status: 当前稿件状态
            user_role: 用户角色
            
        Returns:
            允许执行的动作列表
        """
        allowed_actions = []
        
        # 检查每个动作
        for action in WorkflowAction:
            action_value = action.value
            
            # 检查用户是否有该动作的权限
            if user_role not in ACTION_PERMISSIONS.get(action_value, []):
                continue
            
            # 特殊处理撤稿动作
            if action_value == WorkflowAction.WITHDRAW.value:
                if current_status in WITHDRAWABLE_STATUSES:
                    allowed_actions.append(action_value)
                continue
            
            # 检查是否存在从当前状态出发的转换
            for (status, act, _), _ in TRANSITION_MAP.items():
                if status == current_status and act == action_value:
                    allowed_actions.append(action_value)
                    break
        
        return allowed_actions
    
    @staticmethod
    def get_next_status(
        current_status: str, 
        action: str, 
        decision_type: Optional[str] = None
    ) -> Optional[str]:
        """获取下一个状态
        
        Args:
            current_status: 当前状态
            action: 执行的动作
            decision_type: 决策类型（decide 动作需要）
            
        Returns:
            下一个状态，如果转换不合法则返回 None
        """
        # 撤稿特殊处理
        if action == WorkflowAction.WITHDRAW.value:
            if current_status in WITHDRAWABLE_STATUSES:
                return ManuscriptStatus.WITHDRAWN.value
            return None
        
        # 先尝试带决策类型的转换
        if decision_type:
            key = (current_status, action, decision_type)
            if key in TRANSITION_MAP:
                return TRANSITION_MAP[key]
        
        # 再尝试不带决策类型的转换
        key = (current_status, action, None)
        if key in TRANSITION_MAP:
            return TRANSITION_MAP[key]
        
        return None
    
    @staticmethod
    def get_stage_for_status(status: str) -> str:
        """根据状态获取对应的流转阶段
        
        Args:
            status: 稿件状态
            
        Returns:
            流转阶段
        """
        if status in ManuscriptStatus.get_status_by_phase(ReviewStage.INITIAL_REVIEW):
            return ReviewStage.INITIAL_REVIEW.value
        elif status in ManuscriptStatus.get_status_by_phase(ReviewStage.PEER_REVIEW):
            return ReviewStage.PEER_REVIEW.value
        elif status in ManuscriptStatus.get_status_by_phase(ReviewStage.FINAL_DECISION):
            return ReviewStage.FINAL_DECISION.value
        else:
            # 录用出版阶段和其他状态保持 final_decision
            return ReviewStage.FINAL_DECISION.value
    
    @staticmethod
    def validate_permission(action: str, user_role: str) -> bool:
        """验证用户是否有执行该动作的权限
        
        Args:
            action: 动作
            user_role: 用户角色
            
        Returns:
            是否有权限
        """
        allowed_roles = ACTION_PERMISSIONS.get(action, [])
        return user_role in allowed_roles
    
    @staticmethod
    async def execute_action(
        manuscript_id: int, 
        action: str, 
        user_id: int, 
        user_role: str, 
        session: AsyncSession,
        decision_type: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> dict:
        """执行状态转换
        
        Args:
            manuscript_id: 稿件 ID
            action: 动作
            user_id: 用户 ID
            user_role: 用户角色
            session: 数据库会话
            decision_type: 决策类型（decide 动作需要）
            comment: 备注
            
        Returns:
            操作结果字典
            
        Raises:
            ValueError: 如果稿件不存在、权限不足或状态转换不合法
        """
        # 查询稿件
        query = select(Manuscript).where(
            Manuscript.manuscript_id == manuscript_id,
            Manuscript.is_deleted == False
        )
        result = await session.execute(query)
        manuscript = result.scalar_one_or_none()
        
        if not manuscript:
            raise ValueError("稿件不存在")
        
        current_status = manuscript.status
        
        # 验证权限
        if not ManuscriptWorkflowService.validate_permission(action, user_role):
            raise ValueError(f"用户角色 {user_role} 无权执行动作 {action}")
        
        # 对于作者的撤稿和修改操作，检查是否是本人的稿件
        if action in [WorkflowAction.WITHDRAW.value, WorkflowAction.REVISE.value]:
            if user_role in [UserRole.AUTHOR.value, UserRole.USER.value]:
                if manuscript.author_uid != user_id:
                    raise ValueError("只能操作自己的稿件")
        
        # 决策动作需要决策类型
        if action == WorkflowAction.DECIDE.value and not decision_type:
            raise ValueError("决策动作需要指定决策类型 (accept/reject/revision/transfer)")
        
        # 获取下一个状态
        next_status = ManuscriptWorkflowService.get_next_status(
            current_status, action, decision_type
        )
        
        if not next_status:
            raise ValueError(
                f"状态转换不合法: {current_status} + {action}"
                + (f" + {decision_type}" if decision_type else "")
            )
        
        # 执行状态更新
        old_status = manuscript.status
        old_stage = manuscript.stage
        
        manuscript.status = next_status
        manuscript.stage = ManuscriptWorkflowService.get_stage_for_status(next_status)
        manuscript.update_time = datetime.now().isoformat()
        
        # 如果是修改后重新提交，版本号 +1
        if action == WorkflowAction.REVISE.value:
            manuscript.version += 1
        
        await session.flush()
        
        return {
            "success": True,
            "manuscript_id": manuscript_id,
            "action": action,
            "decision_type": decision_type,
            "old_status": old_status,
            "new_status": next_status,
            "old_stage": old_stage,
            "new_stage": manuscript.stage,
            "version": manuscript.version,
            "update_time": manuscript.update_time,
        }


# 导出服务实例
manuscript_workflow_service = ManuscriptWorkflowService()
