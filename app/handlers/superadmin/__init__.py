from aiogram import Router

from app.handlers.superadmin import (
    start,
    profile,
    registryof_admins
)


def setup(router: Router) -> None:
    for module in (
        profile,
        registryof_admins,
        start
    ):
        router.include_router(module.router)