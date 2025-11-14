from typing import Any, Self

from advanced_alchemy.base import AdvancedDeclarativeBase, CommonTableAttributes
from advanced_alchemy.mixins import AuditColumns, UUIDv7PrimaryKey
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncAttrs


class NoIDSQLModel(
    CommonTableAttributes, AuditColumns, AdvancedDeclarativeBase, AsyncAttrs
):
    __abstract__ = True

    @classmethod
    def from_obj(cls, obj: dict[str, Any]) -> Self:
        new = cls()
        for key, value in obj.items():
            setattr(new, key, value)
        return new

    @classmethod
    def from_pydantic(cls, obj: BaseModel, **kwargs: Any) -> Self:
        return cls.from_obj(obj.model_dump(**kwargs))


class BaseSQLModel(UUIDv7PrimaryKey, NoIDSQLModel):
    __abstract__ = True
