from dishka import Provider, Scope, from_context, provide
from telethon import TelegramClient
from telethon.events.common import EventCommon

from config import BotSettings


class RootProvider(Provider):
    event = from_context(EventCommon, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    def provide_bot_settings(self) -> BotSettings:
        return BotSettings()

    @provide(scope=Scope.REQUEST)
    def provide_telethon_client(self, event: EventCommon) -> TelegramClient:
        return event.client
