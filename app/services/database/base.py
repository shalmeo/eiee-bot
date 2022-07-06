from sqlalchemy import TIMESTAMP, Column, func, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import declarative_mixin

Base = declarative_base()


@declarative_mixin
class TimeStampMixin:
    __abstract__ = True

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


@declarative_mixin
class AccessMixin:
    __abstract__ = True

    access_start = Column(Date, nullable=False)
    access_end = Column(Date, nullable=False)
