from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database.models import Administrator, Student, Teacher

class DefaultRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def user_is_admin(self, user_id: int) -> bool:
        return bool(await self.session.get(Administrator, user_id))
    
    async def user_is_student(self, user_id: int) -> bool:
        return bool(await self.session.get(Student, user_id))
    
    async def user_is_teacher(self, user_id: int) -> bool:
        return bool(await self.session.get(Teacher, user_id))
    
    