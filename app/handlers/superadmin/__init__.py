from aiogram import Router

from app.handlers.superadmin import (
    start,
    profile,
    registryof_admins,
    registryof_teachers,
    registryof_students,
    registryof_groups
)


def setup(router: Router) -> None:
    for module in (
        profile,
        registryof_admins,
        registryof_teachers,
        registryof_students,
        registryof_groups,
        start
    ):
        router.include_router(module.router)