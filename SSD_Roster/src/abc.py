from __future__ import annotations


__all__ = (
    "DBBaseModel",
    "GroupedScopeStr",
)


# third party
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import registry as sa_registry
from sqlalchemy.sql import Delete, Insert, Select, Update
from sqlalchemy.sql.expression import delete, insert, select, update

# typing
from typing import Any, ParamSpec


_P = ParamSpec("_P", bound=Any)


class DBBaseModel(metaclass=DeclarativeMeta):
    __tablename__: str
    __abstract__ = True
    registry: sa_registry = sa_registry()
    metadata: MetaData = registry.metadata
    __init__ = registry.constructor

    # may add more sometime
    @classmethod
    def insert(cls) -> Insert:
        return insert(cls)

    @classmethod
    def select(cls) -> Select:
        return select(cls)

    @classmethod
    def update(cls) -> Update:
        return update(cls)

    @classmethod
    def delete(cls) -> Delete:
        return delete(cls)


class GroupedScopeStr(str):  # yeah... not really an ABC, but will leave it here...
    name: str
    """Name of the group."""

    def __new__(cls, name: str, scopes: str, doc: str):
        self = super().__new__(cls, scopes)
        self.name = name
        self.__str__ = scopes.__str__
        self.__doc__ = doc
        return self
