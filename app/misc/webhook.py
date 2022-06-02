from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.config_reader import Settings


async def setup_webhook(bot: Bot, config: Settings) -> None:
    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_webhook(
        url=config.webhook.url,
    )


def create_app(dispatcher: Dispatcher, bot: Bot, config: Settings) -> web.Application:
    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot
    ).register(
        app,
        path=config.webhook.path
    )
    setup_application(app, dispatcher, bot=bot)
    
    return app
    
    
async def setup_app_runner(app: web.Application) -> web.AppRunner:
    runner = web.AppRunner(app)
    await runner.setup()
    
    return runner
