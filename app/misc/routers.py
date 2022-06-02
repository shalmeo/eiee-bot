from aiogram import Dispatcher, Router

from app.filters.admin.default import DefaultAdminFilter
from app.filters.student.default import DefaultStudentFilter
from app.filters.superadmin.default import DefaultSuperAdminFilter
from app.filters.teacher.default import DefaultTeacherFilter


def create_superadmin_router(dispatcher: Dispatcher):
    router = Router()
    router.message.filter(DefaultSuperAdminFilter())
    router.callback_query.filter(DefaultSuperAdminFilter())
    dispatcher.include_router(router)
    
    return router

def create_admin_router(dispatcher: Dispatcher) -> Router:
    router = Router()
    router.message.filter(DefaultAdminFilter())
    router.callback_query.filter(DefaultAdminFilter())
    dispatcher.include_router(router)
    
    return router


def create_teacher_router(dispatcher: Dispatcher) -> Router:
    router = Router()
    router.message.filter(DefaultTeacherFilter())
    router.callback_query.filter(DefaultTeacherFilter())
    dispatcher.include_router(router)
    
    return router


def create_student_router(dispatcher: Dispatcher) -> Router:
    router = Router()
    router.message.filter(DefaultStudentFilter())
    router.callback_query.filter(DefaultStudentFilter())
    dispatcher.include_router(router)
    
    return router