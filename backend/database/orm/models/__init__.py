"""
ORM Model 注册入口

使用方式：
- DatabaseManager 在建表/迁移前需要 import 本包，以确保所有模型已注册到 Base.metadata。
"""

from database.orm.models.admin_log import AdminLog
from database.orm.models.deleted_journal import DeletedJournal
from database.orm.models.invitation import InvitationCode, InvitationCodeUsage
from database.orm.models.journal import Journal, ReviewRecord
from database.orm.models.journal_info import JournalInfo
from database.orm.models.payment_order import PaymentOrder
from database.orm.models.review_opinion import ReviewOpinion
from database.orm.models.user import User

__all__ = [
    "User",
    "Journal",
    "ReviewRecord",
    "AdminLog",
    "DeletedJournal",
    "JournalInfo",
    "ReviewOpinion",
    "InvitationCode",
    "InvitationCodeUsage",
    "PaymentOrder",
]

