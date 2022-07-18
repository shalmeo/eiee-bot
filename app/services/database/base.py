from sqlalchemy import TIMESTAMP, Column, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import declarative_mixin
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime


Base = declarative_base()


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@declarative_mixin
class TimeStampMixin:
    __abstract__ = True

    created_at = Column(TIMESTAMP(timezone=True), server_default=utcnow())


@declarative_mixin
class AccessMixin:
    __abstract__ = True

    access_start = Column(Date)
    access_end = Column(Date)
