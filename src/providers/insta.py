import asyncio
from pathlib import Path

from dishka import Provider, Scope, provide
from instagrapi import Client

from config import InstaSettings
from services.insta_service import InstaService


class InstaProvider(Provider):
    LOGIN_JSON_PATH = Path("InstagramSession.json")

    @provide(scope=Scope.APP)
    def provide_insta_config(self) -> InstaSettings:
        return InstaSettings()

    @provide(scope=Scope.APP)
    async def provide_insta_client(self, insta_config: InstaSettings) -> Client:
        client = Client()
        await asyncio.to_thread(self.__login, client, insta_config)
        return client

    def __login(self, client: Client, insta_config: InstaSettings) -> None:
        if self.LOGIN_JSON_PATH.exists() and self.LOGIN_JSON_PATH.is_file():
            client.load_settings(self.LOGIN_JSON_PATH)
        client.login(
            username=insta_config.USERNAME,
            password=insta_config.PASSWORD,
            verification_code="",
        )
        client.dump_settings(self.LOGIN_JSON_PATH)
        client.get_timeline_feed()

    @provide(scope=Scope.REQUEST)
    def provide_insta_service(self, insta_client: Client) -> InstaService:
        return InstaService(insta_client=insta_client)
