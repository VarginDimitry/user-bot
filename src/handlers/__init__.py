from handlers.gpt import gpt_router
from handlers.help import help_router
from handlers.insta import insta_router
from handlers.voice import voice_router
from utils.telethon.router import UpdateRouter


def get_main_router() -> UpdateRouter:
    router = UpdateRouter()
    router.include_router(help_router)
    router.include_router(voice_router)
    router.include_router(gpt_router)
    router.include_router(insta_router)
    return router
