from aiogram import Router

from app.handlers.admin import (
    start,
    profile,
    registryof_groups,
    registryof_teachers,
    registryof_students
)

def setup(router: Router) -> None:
    for module in (
        profile,
        registryof_groups,
        registryof_teachers,
        registryof_students,
        start
    ):
        router.include_router(module.router)