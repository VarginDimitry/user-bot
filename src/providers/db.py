import logging
from typing import AsyncIterable

from dishka import provide, Provider, Scope
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from config import Config
from utils.db import json_serializer


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_engine(self, config: Config) -> AsyncEngine:
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
        sqlalchemy_logger.propagate = False
        return create_async_engine(
            str(config.postgres.dns),
            echo=config.postgres.echo,
            pool_size=config.postgres.max_pool_size,
            json_serializer=json_serializer,
        )

    @provide(scope=Scope.APP)
    def provide_session_maker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def provide_session_with_transaction(
        self,
        session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with (
            session_maker() as session,  # pyrefly: ignore[bad-context-manager]
            session.begin(),  # pyrefly: ignore[missing-attribute]
        ):
            exc: Exception | None = yield session
            if exc is not None:
                await session.rollback()  # pyrefly: ignore[missing-attribute]
