from aiohttp import web

from app.endpoints.reg_admin import admin_register_view, admin_register
from app.endpoints.reg_student import student_register, student_register_view
from app.endpoints.reg_teacher import teacher_register, teacher_register_view


def setup(app: web.Application) -> None:
    app.router.add_get('/administrator/reg-form', admin_register_view)
    app.router.add_post('/administrator/register', admin_register)
    
    app.router.add_get('/teacher/reg-form', teacher_register_view)
    app.router.add_post('/teacher/register', teacher_register)
    
    app.router.add_get('/student/reg-form', student_register_view)
    app.router.add_post('/student/register', student_register)