"""
SQLAlchemy ORM 基础设施

本模块仅负责定义 ORM 的 Declarative Base 与通用命名约定。

设计目标：
1. 统一 Metadata，便于集中建表与迁移；
2. 统一命名约定，避免跨数据库的约束/索引命名冲突；
3. 与 FastAPI 的异步调用方式兼容（AsyncSession）。
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

_NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    项目统一 Declarative Base。

    所有 ORM Model 必须继承该 Base，以保证建表与会话管理一致。
    """

    metadata = MetaData(naming_convention=_NAMING_CONVENTION)
