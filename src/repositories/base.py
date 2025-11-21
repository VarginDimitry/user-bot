from advanced_alchemy.filters import ModelT, StatementFilter
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import ColumnElement, text

from utils.filters import FiltersModel


class BaseRepository(SQLAlchemyAsyncRepository[ModelT]):

    async def _lock_wait(self, key: str) -> None:
        stmt = text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))")
        await self.session.execute(stmt, {"key": key})

    async def _lock_nowait(
        self,
        key: str,
    ) -> bool:
        stmt = text("SELECT pg_try_advisory_xact_lock(hashtextextended(:key, 0))")
        result = await self.session.execute(stmt, {"key": key})
        return bool(result.scalar())

    def build_filters(
        self,
        filters: FiltersModel,
        exclude: set[str] | None = None,
    ) -> list[StatementFilter | ColumnElement[bool]]:
        result = []
        for key, value in filters.get_filter_dict().items():
            if exclude and key in exclude:
                continue
            result.append(value.build_filter(getattr(self.model_type, key)))

        return result
