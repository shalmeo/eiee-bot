from aiogram import Router

from app.handlers.superadmin import (
    profile,
    registryof_admins,
    registryof_groups,
    registryof_students,
    registryof_teachers,
    unreg_users,
    start,
)


def setup(router: Router) -> None:
    for module in (
        profile,
        registryof_admins,
        registryof_teachers,
        registryof_students,
        registryof_groups,
        unreg_users,
        start,
    ):
        router.include_router(module.router)
