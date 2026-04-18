"""
全局枚举常量定义

本模块包含系统所有枚举类型，用于统一字段值、状态码、角色等常量定义。
所有枚举值均采用小写英文 snake_case 格式，与前端保持一致。
"""
from enum import Enum, IntEnum


class UserRole(str, Enum):
    """
    用户角色枚举
    
    角色层级（从高到低）：
    admin > editor > associate_editor > ea_ae > reviewer > author > user
    
    说明：
    - admin: 系统管理员，最高权限，负责系统配置、用户管理、数据备份等
    - editor: 正式编辑，核心功能是终审判定、全流程统筹、团队权限分配
    - associate_editor: 副编辑，核心功能是稿件初筛、推荐审稿人、审核评审意见
    - ea_ae: 编辑助理/顾问编辑，辅助操作为主，负责流程文书处理、进度跟进
    - reviewer: 审稿人，根据编辑推荐进行评审，评估稿件质量
    - author: 作者，提交稿件、管理个人信息、与编辑沟通
    - user: 普通用户，浏览期刊内容、注册账号、登录系统
    """
    ADMIN = "admin"
    EDITOR = "editor"
    ASSOCIATE_EDITOR = "associate_editor"
    EA_AE = "ea_ae"
    REVIEWER = "reviewer"
    AUTHOR = "author"
    USER = "user"
    
    @classmethod
    def get_role_level(cls, role: str) -> int:
        """
        获取角色层级级别（数字越大级别越高）
        
        Args:
            role: 角色字符串
            
        Returns:
            角色层级数字，未知角色返回 -1
        """
        level_map = {
            cls.USER: 0,
            cls.AUTHOR: 1,
            cls.REVIEWER: 2,
            cls.EA_AE: 3,
            cls.ASSOCIATE_EDITOR: 4,
            cls.EDITOR: 5,
            cls.ADMIN: 6,
        }
        return level_map.get(role, -1)
    
    @classmethod
    def has_permission(cls, current_role: str, required_role: str) -> bool:
        """
        判断当前角色是否具有所需权限
        
        Args:
            current_role: 当前用户角色
            required_role: 所需的最低角色
            
        Returns:
            True 如果当前角色级别 >= 所需角色级别
        """
        current_level = cls.get_role_level(current_role)
        required_level = cls.get_role_level(required_role)
        return current_level >= required_level and current_level >= 0 and required_level >= 0
    
    @classmethod
    def get_all_values(cls) -> list[str]:
        """返回所有角色值列表"""
        return [role.value for role in cls]

    @classmethod
    def get_assignable_roles(cls) -> list[str]:
        """返回可通过邀请码分配的角色（排除 admin，admin 不应通过邀请码创建）"""
        return [role.value for role in cls if role != cls.ADMIN]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """校验角色值是否合法"""
        return value in cls.get_all_values()


class ReviewStage(str, Enum):
    """
    稿件流转阶段枚举
    
    说明：
    - initial_review: 初审，稿件提交后的初步筛选
    - peer_review: 复审/同行评审，分配给审稿人进行评审
    - final_decision: 终审，编辑最终决策阶段
    """
    INITIAL_REVIEW = "initial_review"
    PEER_REVIEW = "peer_review"
    FINAL_DECISION = "final_decision"
    
    @classmethod
    def get_all_stages(cls) -> list[str]:
        """获取所有阶段值的列表"""
        return [stage.value for stage in cls]


class ManuscriptStatus(str, Enum):
    """
    稿件全局状态枚举
    
    按照稿件流转流程分组：
    1. 初审阶段 (5 个)
    2. 同行评审阶段 (6 个)
    3. 终审阶段 (5 个)
    4. 录用出版阶段 (5 个)
    5. 其他状态 (4 个)
    
    总计：25 个状态值
    """
    
    # ========== 初审阶段 ==========
    PENDING_INITIAL_REVIEW = "pending_initial_review"  # 待初审
    UNDER_INITIAL_REVIEW = "under_initial_review"  # 初审中
    INITIAL_REVIEW_PASSED = "initial_review_passed"  # 初审通过
    INITIAL_REVIEW_REVISION = "initial_review_revision"  # 初审退回修改
    INITIAL_REVIEW_REJECTED = "initial_review_rejected"  # 初审拒稿
    
    # ========== 同行评审阶段 ==========
    PENDING_PEER_REVIEW = "pending_peer_review"  # 待同行评审
    UNDER_PEER_REVIEW = "under_peer_review"  # 评审中
    REVIEW_COMPLETED = "review_completed"  # 评审完成
    REVISION_REQUIRED = "revision_required"  # 需要修稿
    REVISION_SUBMITTED = "revision_submitted"  # 修订稿已提交
    
    # ========== 终审阶段 ==========
    PENDING_FINAL_DECISION = "pending_final_decision"  # 待终审
    UNDER_FINAL_DECISION = "under_final_decision"  # 终审中
    FINAL_DECISION_ACCEPTED = "final_decision_accepted"  # 终审通过
    FINAL_DECISION_REVISION = "final_decision_revision"  # 终审修改后录用
    FINAL_DECISION_REJECTED = "final_decision_rejected"  # 终审拒稿
    
    # ========== 录用出版阶段 ==========
    PENDING_ACCEPTANCE_CONFIRMATION = "pending_acceptance_confirmation"  # 待录用确认
    PENDING_COPYRIGHT = "pending_copyright"  # 待版权协议
    PENDING_PROOF = "pending_proof"  # 待校样确认
    PENDING_PUBLICATION = "pending_publication"  # 待出版
    PUBLISHED = "published"  # 已出版
    
    # ========== 其他状态 ==========
    WITHDRAWN = "withdrawn"  # 已撤稿
    TRANSFER_SUGGESTED = "transfer_suggested"  # 建议转投
    TRANSFERRED = "transferred"  # 已转投
    
    @classmethod
    def get_status_by_phase(cls, phase: ReviewStage) -> list[str]:
        """
        根据流转阶段获取该阶段下的所有状态
        
        Args:
            phase: 流转阶段
            
        Returns:
            该阶段下的所有状态值列表
        """
        phase_status_map = {
            ReviewStage.INITIAL_REVIEW: [
                cls.PENDING_INITIAL_REVIEW.value,
                cls.UNDER_INITIAL_REVIEW.value,
                cls.INITIAL_REVIEW_PASSED.value,
                cls.INITIAL_REVIEW_REVISION.value,
                cls.INITIAL_REVIEW_REJECTED.value,
            ],
            ReviewStage.PEER_REVIEW: [
                cls.PENDING_PEER_REVIEW.value,
                cls.UNDER_PEER_REVIEW.value,
                cls.REVIEW_COMPLETED.value,
                cls.REVISION_REQUIRED.value,
                cls.REVISION_SUBMITTED.value,
            ],
            ReviewStage.FINAL_DECISION: [
                cls.PENDING_FINAL_DECISION.value,
                cls.UNDER_FINAL_DECISION.value,
                cls.FINAL_DECISION_ACCEPTED.value,
                cls.FINAL_DECISION_REVISION.value,
                cls.FINAL_DECISION_REJECTED.value,
            ],
        }
        return phase_status_map.get(phase, [])
    
    @classmethod
    def get_all_statuses(cls) -> list[str]:
        """获取所有状态值的列表"""
        return [status.value for status in cls]


class InvitationStatus(str, Enum):
    """
    邀请码状态枚举
    
    说明：
    - active: 激活状态，可正常使用
    - disabled: 禁用状态，不可使用
    - expired: 过期状态，不可使用
    """
    ACTIVE = "active"
    DISABLED = "disabled"
    EXPIRED = "expired"
    
    @classmethod
    def get_all_statuses(cls) -> list[str]:
        """获取所有状态值的列表"""
        return [status.value for status in cls]


class FileContentType(str, Enum):
    """
    文件内容类型枚举
    
    说明：支持的文件 MIME 类型
    """
    PDF = "application/pdf"
    WORD = "application/msword"
    WORDX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    @classmethod
    def get_allowed_types(cls) -> list[str]:
        """获取允许的文件类型列表"""
        return [content_type.value for content_type in cls]
    
    @classmethod
    def is_allowed(cls, content_type: str) -> bool:
        """
        判断文件类型是否被允许
        
        Args:
            content_type: 文件 MIME 类型
            
        Returns:
            True 如果类型在允许列表中
        """
        return content_type in cls.get_allowed_types()


class WorkflowAction(str, Enum):
    """
    稿件流转动作枚举
    
    说明：
    稿件流转核心接口支持的动作，每个动作对应不同的业务逻辑
    
    动作列表：
    - save: 保存草稿
    - submit: 提交稿件
    - withdraw: 撤稿
    - screen: 初审筛选
    - assign: 分配审稿人
    - review: 提交评审意见
    - decide: 编辑决策
    - revise: 请求修改
    - approve: 录用确认
    - publish: 出版
    """
    SAVE = "save"
    SUBMIT = "submit"
    WITHDRAW = "withdraw"
    SCREEN = "screen"
    ASSIGN = "assign"
    REVIEW = "review"
    DECIDE = "decide"
    REVISE = "revise"
    APPROVE = "approve"
    PUBLISH = "publish"
    
    @classmethod
    def get_all_actions(cls) -> list[str]:
        """获取所有动作值的列表"""
        return [action.value for action in cls]


class DecisionType(str, Enum):
    """
    决策类型枚举
    
    说明：用于记录编辑决策的类型
    """
    ACCEPT = "accept"  # 接受
    REJECT = "reject"  # 拒稿
    REVISION = "revision"  # 修改后录用
    TRANSFER = "transfer"  # 转投
    
    @classmethod
    def get_all_types(cls) -> list[str]:
        """获取所有决策类型的列表"""
        return [dtype.value for dtype in cls]


class NotificationType(str, Enum):
    """
    通知类型枚举
    
    说明：系统通知的分类
    """
    SYSTEM = "system"  # 系统通知
    REVIEW_INVITATION = "review_invitation"  # 审稿邀请
    DECISION = "decision"  # 决策通知
    REVISION = "revision"  # 修改通知
    ACCEPTANCE = "acceptance"  # 录用通知
    PAYMENT = "payment"  # 缴费通知
    
    @classmethod
    def get_all_types(cls) -> list[str]:
        """获取所有通知类型的列表"""
        return [ntype.value for ntype in cls]
