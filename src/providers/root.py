from dishka import Provider, Scope, from_context, provide
from telethon.events.common import EventCommon

from config import BotSettings


class RootProvider(Provider):
    event = from_context(EventCommon, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    def provide_bot_settings(self) -> BotSettings:
        return BotSettings()
