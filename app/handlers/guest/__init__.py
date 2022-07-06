from aiogram import Router

from app.handlers.guest import start, register, log_in


def setup(router: Router) -> None:
    for module in (register, start, log_in):
        router.include_router(module.router)
