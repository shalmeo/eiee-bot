from typing import Iterable

from aiogram import Router

from app.handlers import superadmin, admin, teacher, student


def setup(routers: Iterable[Router]) -> None:
    for packet, router in zip(
        (
            superadmin,
            admin, 
            teacher,
            student
        ),
        routers 
    ):
        packet.setup(router)
    
    
    