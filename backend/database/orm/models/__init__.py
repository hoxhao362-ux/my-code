"""
ORM Model 注册入口

使用方式：
- DatabaseManager 在建表/迁移前需要 import 本包，以确保所有模型已注册到 Base.metadata。
"""

from database.orm.models.admin_log import AdminLog
from database.orm.models.editorial import DecisionRecord, EditorialBoard
from database.orm.models.invitation import InvitationCode, InvitationCodeUsage
from database.orm.models.manuscript import (Manuscript, ManuscriptFile,
                                            ManuscriptParticipant,
                                            ManuscriptVersion)
from database.orm.models.manuscript_info import ManuscriptInfo
from database.orm.models.notification import Notification
from database.orm.models.payment_order import PaymentOrder
from database.orm.models.review_opinion import ReviewOpinion
from database.orm.models.user import User

__all__ = [
    # 用户与权限
    "User",
    "InvitationCode",
    "InvitationCodeUsage",
    # 稿件管理（主力模型）
    "Manuscript",
    "ManuscriptVersion",
    "ManuscriptParticipant",
    "ManuscriptFile",
    "ManuscriptInfo",
    # 通知
    "Notification",
    # 审稿与决策
    "ReviewOpinion",
    "DecisionRecord",
    # 编委会
    "EditorialBoard",
    # 日志与支付
    "AdminLog",
    "PaymentOrder",
]
