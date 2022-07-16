from aiogram import Router
from app.handlers.student import (
    current_tasks,
    profile,
    start,
    in_check_works,
    accepted_works,
    overdue_tasks,
)


def setup(router: Router) -> None:
    for module in (
        current_tasks,
        in_check_works,
        accepted_works,
        overdue_tasks,
        profile,
        start,
    ):
        router.include_router(module.router)
