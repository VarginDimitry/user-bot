from advanced_alchemy.filters import ModelT, StatementFilter
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import bindparam, ColumnElement, func, literal, select, String

from utils.filters import FiltersModel


class BaseRepository(SQLAlchemyAsyncRepository[ModelT]):
    # async def lock_wait(self, order_id: str) -> None:
    #     sql = "SELECT pg_advisory_xact_lock(hashtextextended('payment.order_id'  $1::text, 0))"
    #     await db_context.connection.fetchval(sql, order_id)
    #
    # async def lock_nowait(self, order_id: str,) -> bool:
    #     sql = "SELECT pg_try_advisory_xact_lock(hashtextextended('payment.order_id'  $1::text, 0))"
    #     result = await db_context.connection.fetchval(sql, order_id)
    #     return bool(result)

    async def _lock_wait(self, key: str) -> None:
        stmt = select(
            func.pg_advisory_xact_lock(
                func.hashtextextended(bindparam("key", type_=String), literal(0))
            )
        )
        await self.session.execute(stmt, {"key": key})

    async def _lock_nowait(
        self,
        key: str,
    ) -> bool:
        stmt = select(
            func.pg_try_advisory_xact_lock(
                func.hashtextextended(bindparam("key", type_=String), literal(0))
            )
        )
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
