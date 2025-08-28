from logging import Logger

from dishka import provide, Provider, Scope

from config import RootConfig
from services.insta_service import InstaService


class InstaProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_insta_service(
        self,
        logger: Logger,
        config: RootConfig,
    ) -> InstaService:
        return InstaService(
            logger=logger,
            config=config,
        )
