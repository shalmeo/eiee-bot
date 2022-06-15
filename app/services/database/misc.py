import datetime

from sqlalchemy.orm import sessionmaker

from app.services.database.models import Administrator


async def add_initial_admin(session_factory: sessionmaker, admin_id: int) -> None:
    async with session_factory() as session:
        if not await session.get(Administrator, admin_id):
            session.add(
                Administrator(
                    id=admin_id,
                    first_name="Admin",
                    last_name="Super",
                    patronymic="None",
                    email="None",
                    user_name="None",
                    tel=0,
                    level="None",
                    description="None",
                    timezone="None",
                    access_start=datetime.date.today(),
                    access_end=datetime.date.today(),
                )
            )
            await session.commit()
