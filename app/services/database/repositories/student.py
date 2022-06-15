from typing import Iterable, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class StudentRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, entity: T, ident: int) -> T:
        return await self.session.get(entity, ident)
