from logging import Logger

from dishka import provide, Provider, Scope
from instagrapi import Client

from config import RootConfig
from services.insta_service import InstaService


class InstaProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_insta_client(self, config: RootConfig, logger: Logger) -> Client:
        return Client(
            delay_range=[config.instagram.delay_from, config.instagram.delay_to],
            logger=logger.getChild("instagrapi"),
        )

    @provide(scope=Scope.REQUEST)
    async def provide_insta_service(
        self,
        logger: Logger,
        config: RootConfig,
        insta_client: Client,
    ) -> InstaService:
        service = InstaService(
            logger=logger,
            insta_client=insta_client,
            config=config,
        )
        if not await service.login():
            raise Exception("Failed to login to Instagram")
        return service
