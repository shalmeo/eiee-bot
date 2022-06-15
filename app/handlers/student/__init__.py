from aiogram import Router

from app.handlers.student import (
    start,
    my_groups,
    profile
)

def setup(router: Router) -> None:
    for module in (
        my_groups, 
        profile,
        start
    ):
        router.include_router(module.router)