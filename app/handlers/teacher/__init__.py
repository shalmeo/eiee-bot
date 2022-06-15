from aiogram import Router

from app.handlers.teacher import (
    profile,
    start
)

def setup(router: Router) -> None:
    for module in (
        profile,
        start
    ):
        router.include_router(module.router)