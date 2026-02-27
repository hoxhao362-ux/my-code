"""
支付订单表 ORM Model

表名：payment_orders
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.orm.base import Base


class PaymentOrder(Base):
    __tablename__ = "payment_orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="订单ID（自增）")
    merchant_order_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False, comment="商户订单号（唯一）")
    transaction_id: Mapped[str | None] = mapped_column(Text, nullable=True, comment="支付平台交易号")

    uid: Mapped[int] = mapped_column(Integer, ForeignKey("users.uid"), nullable=False, comment="用户ID")
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, comment="金额")
    currency: Mapped[str] = mapped_column(Text, nullable=False, server_default="CNY", comment="币种")
    subject: Mapped[str] = mapped_column(Text, nullable=False, comment="订单标题/商品描述")

    provider: Mapped[str] = mapped_column(Text, nullable=False, comment="支付提供商（alipay/wechat/paypal/mock...）")
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="pending", comment="状态：pending/paid/refunded/failed/closed")

    create_time: Mapped[str] = mapped_column(Text, nullable=False, comment="创建时间（ISO字符串）")
    update_time: Mapped[str | None] = mapped_column(Text, nullable=True, comment="更新时间（ISO字符串）")

    pay_time: Mapped[str | None] = mapped_column(Text, nullable=True, comment="支付时间（ISO字符串）")
    refund_time: Mapped[str | None] = mapped_column(Text, nullable=True, comment="退款时间（ISO字符串）")
    refund_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, comment="退款金额")
    refund_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="退款原因")

    extra_data: Mapped[str | None] = mapped_column(Text, nullable=True, comment="扩展数据（JSON字符串等）")


Index("idx_payment_orders_merchant_order_id", PaymentOrder.merchant_order_id)
Index("idx_payment_orders_uid", PaymentOrder.uid)
Index("idx_payment_orders_status", PaymentOrder.status)
Index("idx_payment_orders_create_time", PaymentOrder.create_time)

