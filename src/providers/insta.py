from logging import Logger

from dishka import provide, Provider, Scope
from instagrapi import Client

from config import InstaSettings
from services.insta_service import InstaService


class InstaProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_insta_config(self) -> InstaSettings:
        return InstaSettings()

    @provide(scope=Scope.APP)
    def provide_insta_client(self, logger: Logger) -> Client:
        return Client(logger=logger.getChild("instagrapi"))

    @provide(scope=Scope.REQUEST)
    async def provide_insta_service(
        self,
        logger: Logger,
        insta_config: InstaSettings,
        insta_client: Client,
    ) -> InstaService:
        service = InstaService(
            logger=logger,
            insta_client=insta_client,
            config=insta_config,
        )
        if not await service.login():
            raise Exception("Failed to login to Instagram")
        return service
