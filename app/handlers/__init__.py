from typing import Iterable

from aiogram import Router
from app.handlers import admin, guest, student, superadmin, teacher


def setup(routers: Iterable[Router]) -> None:
    for packet, router in zip((superadmin, admin, teacher, student, guest), routers):
        packet.setup(router)
