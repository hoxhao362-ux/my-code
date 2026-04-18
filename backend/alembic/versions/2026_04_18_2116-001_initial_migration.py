"""
初始数据库迁移

创建所有核心表结构：
- users: 用户表
- manuscripts: 稿件主表
- manuscript_versions: 稿件版本表
- manuscript_participants: 稿件参与者表
- manuscript_files: 稿件附件表
- manuscript_info: 稿件出版信息表
- invitation_codes: 邀请码表
- invitation_code_usage: 邀请码使用记录表
- review_opinions: 审稿意见表
- editorial_board: 编委会成员表
- decision_records: 编辑决策记录表
- admin_logs: 管理员操作日志表
- payment_orders: 支付订单表

生成时间: 2026-04-18 21:16:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级数据库结构 - 创建所有表"""

    # =========================================================================
    # 1. 用户表 (users)
    # =========================================================================
    op.create_table(
        "users",
        sa.Column("uid", sa.Integer(), nullable=False, comment="用户ID（自增）"),
        sa.Column(
            "uid_hash", sa.Text(), nullable=False, comment="用户UID哈希（业务唯一）"
        ),
        sa.Column("username", sa.Text(), nullable=False, comment="用户名（唯一）"),
        sa.Column("password", sa.Text(), nullable=False, comment="密码哈希"),
        sa.Column("email", sa.Text(), nullable=False, comment="邮箱（唯一）"),
        sa.Column(
            "role",
            sa.Text(),
            nullable=False,
            server_default="author",
            comment="角色：user/author/reviewer/ea_ae/associate_editor/editor/admin",
        ),
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            comment="是否已验证邮箱/账号",
        ),
        sa.Column("verification_code", sa.Text(), nullable=True, comment="验证码"),
        sa.Column("avatar_path", sa.Text(), nullable=True, comment="头像文件路径"),
        sa.Column("avatar_hash", sa.Text(), nullable=True, comment="头像哈希"),
        sa.Column("create_time", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.Column(
            "last_login_time", sa.DateTime(), nullable=True, comment="最后登录时间"
        ),
        sa.Column(
            "login_days",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="累计登录天数",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            comment="是否已删除（软删除）",
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True, comment="删除时间"),
        sa.PrimaryKeyConstraint("uid", name="pk_users"),
        sa.UniqueConstraint("uid_hash", name="uq_users_uid_hash"),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("idx_users_username", "users", ["username"])
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_is_deleted", "users", ["is_deleted"])

    # =========================================================================
    # 2. 稿件主表 (manuscripts)
    # =========================================================================
    op.create_table(
        "manuscripts",
        sa.Column(
            "manuscript_id",
            sa.BigInteger(),
            nullable=False,
            comment="稿件 ID（自增，BIGSERIAL）",
        ),
        sa.Column(
            "author_uid", sa.Integer(), nullable=False, comment="投稿作者用户 ID"
        ),
        sa.Column("title", sa.Text(), nullable=False, comment="稿件标题"),
        sa.Column(
            "article_type",
            sa.Text(),
            nullable=False,
            server_default="Research Article",
            comment="文章类型",
        ),
        sa.Column("section_category", sa.Text(), nullable=True, comment="栏目/类别"),
        sa.Column(
            "keywords", sa.Text(), nullable=False, server_default="", comment="关键字"
        ),
        sa.Column(
            "first_author",
            sa.Text(),
            nullable=False,
            server_default="",
            comment="第一作者",
        ),
        sa.Column(
            "corresponding_author",
            sa.Text(),
            nullable=False,
            server_default="",
            comment="通讯作者",
        ),
        sa.Column(
            "order_of_authors",
            sa.Text(),
            nullable=False,
            server_default="[]",
            comment="作者排序(JSON格式)",
        ),
        sa.Column(
            "authors",
            sa.Text(),
            nullable=False,
            comment="作者列表（字符串，逗号分隔，向下兼容）",
        ),
        sa.Column("abstract", sa.Text(), nullable=True, comment="摘要"),
        sa.Column("subject", sa.Text(), nullable=False, comment="学科/主题"),
        sa.Column(
            "stage",
            sa.Text(),
            nullable=False,
            server_default="initial_review",
            comment="流转阶段：initial_review/peer_review/final_decision",
        ),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default="pending_initial_review",
            comment="全局状态",
        ),
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default="1",
            comment="版本号",
        ),
        sa.Column("file_hash", sa.Text(), nullable=False, comment="文件哈希（唯一）"),
        sa.Column("file_bucket", sa.Text(), nullable=False, comment="文件存储桶路径"),
        sa.Column("file_name", sa.Text(), nullable=False, comment="原始文件名"),
        sa.Column(
            "file_size", sa.BigInteger(), nullable=False, comment="文件大小（字节）"
        ),
        sa.Column("create_time", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.Column("update_time", sa.DateTime(), nullable=True, comment="更新时间"),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            comment="是否已删除（软删除）",
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True, comment="删除时间"),
        sa.Column("delete_reason", sa.Text(), nullable=True, comment="删除原因"),
        sa.PrimaryKeyConstraint("manuscript_id", name="pk_manuscripts"),
        sa.UniqueConstraint("file_hash", name="uq_manuscripts_file_hash"),
        sa.ForeignKeyConstraint(
            ["author_uid"], ["users.uid"], name="fk_manuscripts_author_uid_users"
        ),
    )
    op.create_index("idx_manuscripts_author_uid", "manuscripts", ["author_uid"])
    op.create_index("idx_manuscripts_stage", "manuscripts", ["stage"])
    op.create_index("idx_manuscripts_status", "manuscripts", ["status"])
    op.create_index("idx_manuscripts_file_hash", "manuscripts", ["file_hash"])
    op.create_index("idx_manuscripts_is_deleted", "manuscripts", ["is_deleted"])

    # =========================================================================
    # 3. 稿件版本表 (manuscript_versions)
    # =========================================================================
    op.create_table(
        "manuscript_versions",
        sa.Column(
            "version_id", sa.BigInteger(), nullable=False, comment="版本 ID（自增）"
        ),
        sa.Column("manuscript_id", sa.BigInteger(), nullable=False, comment="稿件 ID"),
        sa.Column(
            "version_number",
            sa.Integer(),
            nullable=False,
            comment="版本号（从 1 开始）",
        ),
        sa.Column("title", sa.Text(), nullable=False, comment="稿件标题"),
        sa.Column("authors", sa.Text(), nullable=False, comment="作者列表"),
        sa.Column("abstract", sa.Text(), nullable=True, comment="摘要"),
        sa.Column("file_hash", sa.Text(), nullable=False, comment="文件哈希"),
        sa.Column("file_bucket", sa.Text(), nullable=False, comment="文件存储桶路径"),
        sa.Column("file_name", sa.Text(), nullable=False, comment="原始文件名"),
        sa.Column(
            "file_size", sa.BigInteger(), nullable=False, comment="文件大小（字节）"
        ),
        sa.Column(
            "submitted_by_uid", sa.Integer(), nullable=False, comment="提交者用户 ID"
        ),
        sa.Column("submitted_at", sa.DateTime(), nullable=False, comment="提交时间"),
        sa.Column("change_summary", sa.Text(), nullable=True, comment="修改说明"),
        sa.PrimaryKeyConstraint("version_id", name="pk_manuscript_versions"),
        sa.ForeignKeyConstraint(
            ["manuscript_id"],
            ["manuscripts.manuscript_id"],
            name="fk_manuscript_versions_manuscript_id_manuscripts",
        ),
        sa.ForeignKeyConstraint(
            ["submitted_by_uid"],
            ["users.uid"],
            name="fk_manuscript_versions_submitted_by_uid_users",
        ),
    )
    op.create_index(
        "idx_manuscript_versions_manuscript_id",
        "manuscript_versions",
        ["manuscript_id"],
    )
    op.create_index(
        "idx_manuscript_versions_version_number",
        "manuscript_versions",
        ["version_number"],
    )

    # =========================================================================
    # 4. 稿件参与者表 (manuscript_participants)
    # =========================================================================
    op.create_table(
        "manuscript_participants",
        sa.Column(
            "participant_id", sa.Integer(), nullable=False, comment="参与者 ID（自增）"
        ),
        sa.Column("manuscript_id", sa.BigInteger(), nullable=False, comment="稿件 ID"),
        sa.Column("user_uid", sa.Integer(), nullable=False, comment="用户 ID"),
        sa.Column(
            "role_type",
            sa.Text(),
            nullable=False,
            comment="参与角色：author/editor/associate_editor/ea_ae/reviewer",
        ),
        sa.Column("assigned_at", sa.DateTime(), nullable=False, comment="分配时间"),
        sa.Column(
            "assigned_by_uid", sa.Integer(), nullable=False, comment="分配者用户 ID"
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default="true",
            comment="是否活跃",
        ),
        sa.Column("completed_at", sa.DateTime(), nullable=True, comment="完成时间"),
        sa.PrimaryKeyConstraint("participant_id", name="pk_manuscript_participants"),
        sa.ForeignKeyConstraint(
            ["manuscript_id"],
            ["manuscripts.manuscript_id"],
            name="fk_manuscript_participants_manuscript_id_manuscripts",
        ),
        sa.ForeignKeyConstraint(
            ["user_uid"],
            ["users.uid"],
            name="fk_manuscript_participants_user_uid_users",
        ),
        sa.ForeignKeyConstraint(
            ["assigned_by_uid"],
            ["users.uid"],
            name="fk_manuscript_participants_assigned_by_uid_users",
        ),
    )
    op.create_index(
        "idx_manuscript_participants_manuscript_id",
        "manuscript_participants",
        ["manuscript_id"],
    )
    op.create_index(
        "idx_manuscript_participants_user_uid", "manuscript_participants", ["user_uid"]
    )
    op.create_index(
        "idx_manuscript_participants_role_type",
        "manuscript_participants",
        ["role_type"],
    )

    # =========================================================================
    # 5. 稿件附件表 (manuscript_files)
    # =========================================================================
    op.create_table(
        "manuscript_files",
        sa.Column("file_id", sa.Integer(), nullable=False, comment="附件 ID（自增）"),
        sa.Column("manuscript_id", sa.BigInteger(), nullable=False, comment="稿件 ID"),
        sa.Column("file_hash", sa.Text(), nullable=False, comment="文件哈希"),
        sa.Column("file_bucket", sa.Text(), nullable=False, comment="文件存储桶路径"),
        sa.Column("original_name", sa.Text(), nullable=False, comment="原始文件名"),
        sa.Column(
            "file_size", sa.BigInteger(), nullable=False, comment="文件大小（字节）"
        ),
        sa.Column("content_type", sa.Text(), nullable=False, comment="文件 MIME 类型"),
        sa.Column(
            "file_type",
            sa.Text(),
            nullable=False,
            server_default="attachment",
            comment="文件类型：main/review/letter/other",
        ),
        sa.Column(
            "uploaded_by_uid", sa.Integer(), nullable=False, comment="上传者用户 ID"
        ),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False, comment="上传时间"),
        sa.Column("description", sa.Text(), nullable=True, comment="文件描述"),
        sa.PrimaryKeyConstraint("file_id", name="pk_manuscript_files"),
        sa.ForeignKeyConstraint(
            ["manuscript_id"],
            ["manuscripts.manuscript_id"],
            name="fk_manuscript_files_manuscript_id_manuscripts",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by_uid"],
            ["users.uid"],
            name="fk_manuscript_files_uploaded_by_uid_users",
        ),
    )
    op.create_index(
        "idx_manuscript_files_manuscript_id", "manuscript_files", ["manuscript_id"]
    )
    op.create_index("idx_manuscript_files_file_hash", "manuscript_files", ["file_hash"])
    op.create_index("idx_manuscript_files_file_type", "manuscript_files", ["file_type"])

    # =========================================================================
    # 6. 稿件出版信息表 (manuscript_info)
    # =========================================================================
    op.create_table(
        "manuscript_info",
        sa.Column("info_id", sa.Integer(), nullable=False, comment="信息ID（自增）"),
        sa.Column("manuscript_id", sa.BigInteger(), nullable=False, comment="稿件ID"),
        sa.Column(
            "issue_number", sa.Text(), nullable=False, comment="期号（业务字段）"
        ),
        sa.Column(
            "publication_date",
            sa.Text(),
            nullable=False,
            comment="出版日期（ISO字符串）",
        ),
        sa.Column("volume", sa.Text(), nullable=True, comment="卷"),
        sa.Column("issue", sa.Text(), nullable=True, comment="期"),
        sa.Column("journal_type", sa.Text(), nullable=True, comment="期刊类型"),
        sa.Column("keywords", sa.Text(), nullable=True, comment="关键词（字符串）"),
        sa.Column("doi", sa.Text(), nullable=True, comment="DOI"),
        sa.PrimaryKeyConstraint("info_id", name="pk_manuscript_info"),
        sa.ForeignKeyConstraint(
            ["manuscript_id"],
            ["manuscripts.manuscript_id"],
            name="fk_manuscript_info_manuscript_id_manuscripts",
        ),
    )
    op.create_index(
        "idx_manuscript_info_manuscript_id", "manuscript_info", ["manuscript_id"]
    )

    # =========================================================================
    # 7. 邀请码表 (invitation_codes)
    # =========================================================================
    op.create_table(
        "invitation_codes",
        sa.Column("code_id", sa.Integer(), nullable=False, comment="主键ID（自增）"),
        sa.Column("code", sa.Text(), nullable=False, comment="邀请码（唯一）"),
        sa.Column(
            "role",
            sa.Text(),
            nullable=False,
            comment="授予角色：user/author/reviewer/ea_ae/associate_editor/editor/admin",
        ),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default="active",
            comment="状态：active/disabled/expired",
        ),
        sa.Column(
            "max_uses",
            sa.Integer(),
            nullable=False,
            server_default="1",
            comment="最大可使用次数",
        ),
        sa.Column(
            "used_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="已使用次数",
        ),
        sa.Column("description", sa.Text(), nullable=True, comment="描述"),
        sa.Column("created_by", sa.Text(), nullable=False, comment="创建人用户名"),
        sa.Column(
            "created_by_uid", sa.Integer(), nullable=False, comment="创建人用户ID"
        ),
        sa.Column("create_time", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.Column("expire_time", sa.DateTime(), nullable=True, comment="过期时间"),
        sa.PrimaryKeyConstraint("code_id", name="pk_invitation_codes"),
        sa.UniqueConstraint("code", name="uq_invitation_codes_code"),
        sa.ForeignKeyConstraint(
            ["created_by_uid"],
            ["users.uid"],
            name="fk_invitation_codes_created_by_uid_users",
        ),
    )
    op.create_index("idx_invitation_codes_code", "invitation_codes", ["code"])

    # =========================================================================
    # 8. 邀请码使用记录表 (invitation_code_usage)
    # =========================================================================
    op.create_table(
        "invitation_code_usage",
        sa.Column(
            "usage_id", sa.Integer(), nullable=False, comment="使用记录ID（自增）"
        ),
        sa.Column("code", sa.Text(), nullable=False, comment="邀请码"),
        sa.Column("used_by_uid", sa.Integer(), nullable=False, comment="使用人用户ID"),
        sa.Column(
            "used_by_username", sa.Text(), nullable=False, comment="使用人用户名"
        ),
        sa.Column("use_time", sa.DateTime(), nullable=False, comment="使用时间"),
        sa.PrimaryKeyConstraint("usage_id", name="pk_invitation_code_usage"),
        sa.ForeignKeyConstraint(
            ["used_by_uid"],
            ["users.uid"],
            name="fk_invitation_code_usage_used_by_uid_users",
        ),
    )
    op.create_index("idx_invitation_code_usage_code", "invitation_code_usage", ["code"])
    op.create_index(
        "idx_invitation_code_usage_used_by_uid",
        "invitation_code_usage",
        ["used_by_uid"],
    )

    # =========================================================================
    # 9. 审稿意见表 (review_opinions)
    # =========================================================================
    op.create_table(
        "review_opinions",
        sa.Column("opinion_id", sa.Integer(), nullable=False, comment="意见ID（自增）"),
        sa.Column("manuscript_id", sa.BigInteger(), nullable=False, comment="稿件ID"),
        sa.Column("reviewer_uid", sa.Integer(), nullable=False, comment="审稿人用户ID"),
        sa.Column(
            "stage",
            sa.Text(),
            nullable=False,
            comment="审稿阶段：initial_review/peer_review/final_decision",
        ),
        sa.Column(
            "review_round",
            sa.Integer(),
            nullable=False,
            server_default="1",
            comment="审稿轮次",
        ),
        sa.Column("review_score", sa.Integer(), nullable=False, comment="评分"),
        sa.Column("review_comments", sa.Text(), nullable=False, comment="审稿意见"),
        sa.Column("recommendations", sa.Text(), nullable=True, comment="建议"),
        sa.Column(
            "decision",
            sa.Text(),
            nullable=True,
            comment="审稿结论：accept/reject/revision",
        ),
        sa.Column("submitted_at", sa.DateTime(), nullable=False, comment="提交时间"),
        sa.PrimaryKeyConstraint("opinion_id", name="pk_review_opinions"),
        sa.ForeignKeyConstraint(
            ["manuscript_id"],
            ["manuscripts.manuscript_id"],
            name="fk_review_opinions_manuscript_id_manuscripts",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_uid"],
            ["users.uid"],
            name="fk_review_opinions_reviewer_uid_users",
        ),
    )
    op.create_index(
        "idx_review_opinions_manuscript_id", "review_opinions", ["manuscript_id"]
    )
    op.create_index(
        "idx_review_opinions_reviewer_uid", "review_opinions", ["reviewer_uid"]
    )

    # =========================================================================
    # 10. 编委会成员表 (editorial_board)
    # =========================================================================
    op.create_table(
        "editorial_board",
        sa.Column("board_id", sa.Integer(), nullable=False, comment="编委 ID（自增）"),
        sa.Column("user_uid", sa.Integer(), nullable=False, comment="用户 ID"),
        sa.Column(
            "position",
            sa.Text(),
            nullable=False,
            comment="职位：editor/associate_editor/ea_ae",
        ),
        sa.Column("title", sa.Text(), nullable=True, comment="职称/头衔"),
        sa.Column(
            "research_areas", sa.Text(), nullable=True, comment="研究领域（逗号分隔）"
        ),
        sa.Column("appointed_at", sa.DateTime(), nullable=False, comment="任命时间"),
        sa.Column(
            "appointed_by_uid", sa.Integer(), nullable=False, comment="任命者用户 ID"
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default="true",
            comment="是否在职",
        ),
        sa.PrimaryKeyConstraint("board_id", name="pk_editorial_board"),
        sa.UniqueConstraint("user_uid", name="uq_editorial_board_user_uid"),
        sa.ForeignKeyConstraint(
            ["user_uid"], ["users.uid"], name="fk_editorial_board_user_uid_users"
        ),
        sa.ForeignKeyConstraint(
            ["appointed_by_uid"],
            ["users.uid"],
            name="fk_editorial_board_appointed_by_uid_users",
        ),
    )
    op.create_index("idx_editorial_board_user_uid", "editorial_board", ["user_uid"])
    op.create_index("idx_editorial_board_position", "editorial_board", ["position"])
    op.create_index("idx_editorial_board_is_active", "editorial_board", ["is_active"])

    # =========================================================================
    # 11. 编辑决策记录表 (decision_records)
    # =========================================================================
    op.create_table(
        "decision_records",
        sa.Column(
            "decision_id", sa.BigInteger(), nullable=False, comment="决策 ID（自增）"
        ),
        sa.Column("manuscript_id", sa.BigInteger(), nullable=False, comment="稿件 ID"),
        sa.Column(
            "stage",
            sa.Text(),
            nullable=False,
            comment="决策阶段：initial_review/peer_review/final_decision",
        ),
        sa.Column(
            "decision_type",
            sa.Text(),
            nullable=False,
            comment="决策类型：accept/reject/revision/transfer",
        ),
        sa.Column("decision_title", sa.Text(), nullable=False, comment="决策标题"),
        sa.Column("decision_comments", sa.Text(), nullable=False, comment="决策意见"),
        sa.Column("recommendations", sa.Text(), nullable=True, comment="建议"),
        sa.Column(
            "decided_by_uid", sa.Integer(), nullable=False, comment="决策者用户 ID"
        ),
        sa.Column("decided_at", sa.DateTime(), nullable=False, comment="决策时间"),
        sa.PrimaryKeyConstraint("decision_id", name="pk_decision_records"),
        sa.ForeignKeyConstraint(
            ["manuscript_id"],
            ["manuscripts.manuscript_id"],
            name="fk_decision_records_manuscript_id_manuscripts",
        ),
        sa.ForeignKeyConstraint(
            ["decided_by_uid"],
            ["users.uid"],
            name="fk_decision_records_decided_by_uid_users",
        ),
    )
    op.create_index(
        "idx_decision_records_manuscript_id", "decision_records", ["manuscript_id"]
    )
    op.create_index("idx_decision_records_stage", "decision_records", ["stage"])
    op.create_index(
        "idx_decision_records_decided_by_uid", "decision_records", ["decided_by_uid"]
    )

    # =========================================================================
    # 12. 管理员操作日志表 (admin_logs)
    # =========================================================================
    op.create_table(
        "admin_logs",
        sa.Column("log_id", sa.Integer(), nullable=False, comment="日志ID（自增）"),
        sa.Column("admin_uid", sa.Integer(), nullable=False, comment="管理员用户ID"),
        sa.Column("admin_username", sa.Text(), nullable=False, comment="管理员用户名"),
        sa.Column("operation_time", sa.DateTime(), nullable=False, comment="操作时间"),
        sa.Column("operation_type", sa.Text(), nullable=False, comment="操作类型"),
        sa.Column("operation_object", sa.Text(), nullable=False, comment="操作对象"),
        sa.Column("operation_details", sa.Text(), nullable=True, comment="操作详情"),
        sa.Column("ip_address", sa.Text(), nullable=True, comment="IP地址"),
        sa.Column("user_agent", sa.Text(), nullable=True, comment="User-Agent"),
        sa.PrimaryKeyConstraint("log_id", name="pk_admin_logs"),
    )

    # =========================================================================
    # 13. 支付订单表 (payment_orders)
    # =========================================================================
    op.create_table(
        "payment_orders",
        sa.Column("order_id", sa.Integer(), nullable=False, comment="订单ID（自增）"),
        sa.Column(
            "merchant_order_id", sa.Text(), nullable=False, comment="商户订单号（唯一）"
        ),
        sa.Column("transaction_id", sa.Text(), nullable=True, comment="支付平台交易号"),
        sa.Column("uid", sa.Integer(), nullable=False, comment="用户ID"),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False, comment="金额"),
        sa.Column(
            "currency", sa.Text(), nullable=False, server_default="CNY", comment="币种"
        ),
        sa.Column("subject", sa.Text(), nullable=False, comment="订单标题/商品描述"),
        sa.Column(
            "provider",
            sa.Text(),
            nullable=False,
            comment="支付提供商（alipay/wechat/paypal/mock...）",
        ),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default="pending",
            comment="状态：pending/paid/refunded/failed/closed",
        ),
        sa.Column("create_time", sa.DateTime(), nullable=False, comment="创建时间"),
        sa.Column("update_time", sa.DateTime(), nullable=True, comment="更新时间"),
        sa.Column("pay_time", sa.DateTime(), nullable=True, comment="支付时间"),
        sa.Column("refund_time", sa.DateTime(), nullable=True, comment="退款时间"),
        sa.Column(
            "refund_amount", sa.Numeric(10, 2), nullable=True, comment="退款金额"
        ),
        sa.Column("refund_reason", sa.Text(), nullable=True, comment="退款原因"),
        sa.Column(
            "extra_data", sa.Text(), nullable=True, comment="扩展数据（JSON字符串等）"
        ),
        sa.PrimaryKeyConstraint("order_id", name="pk_payment_orders"),
        sa.UniqueConstraint(
            "merchant_order_id", name="uq_payment_orders_merchant_order_id"
        ),
        sa.ForeignKeyConstraint(
            ["uid"], ["users.uid"], name="fk_payment_orders_uid_users"
        ),
    )
    op.create_index(
        "idx_payment_orders_merchant_order_id", "payment_orders", ["merchant_order_id"]
    )
    op.create_index("idx_payment_orders_uid", "payment_orders", ["uid"])
    op.create_index("idx_payment_orders_status", "payment_orders", ["status"])
    op.create_index("idx_payment_orders_create_time", "payment_orders", ["create_time"])


def downgrade() -> None:
    """降级数据库结构 - 删除所有表"""

    # 按照外键依赖的逆序删除表
    op.drop_table("payment_orders")
    op.drop_table("admin_logs")
    op.drop_table("decision_records")
    op.drop_table("editorial_board")
    op.drop_table("review_opinions")
    op.drop_table("invitation_code_usage")
    op.drop_table("invitation_codes")
    op.drop_table("manuscript_info")
    op.drop_table("manuscript_files")
    op.drop_table("manuscript_participants")
    op.drop_table("manuscript_versions")
    op.drop_table("manuscripts")
    op.drop_table("users")
