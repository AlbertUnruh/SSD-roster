__all__ = ("DBBaseModel",)


# third party
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import registry as sa_registry
from sqlalchemy.sql import Insert as sa_Insert
from sqlalchemy.sql import Select
from sqlalchemy.sql.expression import insert, select

# typing
from typing import Any, ParamSpec, Self


_P = ParamSpec("_P", bound=Any)


class _Insert(sa_Insert):
    # the @generative doesn't work with SELF-return for typehints...
    def values(self, *args: Any, **kwargs: Any) -> Self:
        return super().values(*args, **kwargs)


class DBBaseModel(metaclass=DeclarativeMeta):
    __tablename__: str
    __abstract__ = True
    registry: sa_registry = sa_registry()
    metadata: MetaData = registry.metadata
    __init__ = registry.constructor

    # may add more sometime
    @classmethod
    def insert(cls) -> _Insert:
        return insert(cls)

    @classmethod
    def select(cls) -> Select:
        return select(cls)
