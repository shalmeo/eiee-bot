import datetime
from contextlib import suppress

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.services.database.models import Administrator


async def add_initial_admin(session_factory: sessionmaker, admin_id: int) -> None:
    async with session_factory() as session:
        superadmin = Administrator(
            id=0,
            first_name="Admin",
            last_name="Super",
            patronymic="None",
            email="None",
            user_name="None",
            tel=0,
            level="None",
            description="None",
            timezone="UTC+3",
            access_start=datetime.date.today(),
            access_end=datetime.date.today(),
            telegram_id=admin_id,
        )
        session.add(superadmin)
        with suppress(IntegrityError):
            await session.commit()
