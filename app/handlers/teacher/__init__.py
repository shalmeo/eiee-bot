from aiogram import Router
from app.handlers.teacher import profile, start, groups, create_home_task, check_home_works


def setup(router: Router) -> None:
    for module in (profile, groups, create_home_task, check_home_works, start):
        router.include_router(module.router)
