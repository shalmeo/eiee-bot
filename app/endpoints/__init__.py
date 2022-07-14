from aiohttp import web

from app.endpoints.admin import change_admin_info, get_admin, change_admin_info_view
from app.endpoints.change_group import (
    change_group_info_view,
    get_group,
    change_group_info,
)
from app.endpoints.create_group import create_group_form, new_group
from app.endpoints.parents import (
    change_student_parents_info_view,
    get_student_parents,
    change_student_parents_info,
)
from app.endpoints.reg_admin import admin_register_view, admin_register
from app.endpoints.reg_student import student_register, student_register_view
from app.endpoints.reg_teacher import teacher_register, teacher_register_view
from app.endpoints.create_home_task import create_home_task, create_home_task_view
from app.endpoints.student import (
    change_student_info_view,
    change_student_info,
    get_student,
)
from app.endpoints.user_sign_up import user_sign_up_view, user_sign_up
from app.endpoints.students import get_all_students
from app.endpoints.teacher import (
    change_teacher_info_view,
    get_teacher,
    change_teacher_info,
)
from app.endpoints.teachers import get_teachers
from app.endpoints.change_compound import (
    change_compound_view,
    get_students,
    change_compound,
)


def setup(app: web.Application) -> None:
    app.router.add_get("/administrator/reg-form", admin_register_view)
    app.router.add_post("/administrator/register", admin_register)

    app.router.add_get("/teacher/reg-form", teacher_register_view)
    app.router.add_post("/teacher/register", teacher_register)

    app.router.add_get("/student/reg-form", student_register_view)
    app.router.add_post("/student/register", student_register)

    app.router.add_get("/teacher/create-home-task-form", create_home_task_view)
    app.router.add_post("/teacher/create-home-task", create_home_task)

    app.router.add_get("/group/create-form", create_group_form)
    app.router.add_post("/group/create", new_group)

    app.router.add_post("/teachers", get_teachers)

    app.router.add_get("/group/change-compound", change_compound_view)
    app.router.add_post("/group/change-compound", change_compound)
    app.router.add_post("/group/students", get_students)

    app.router.add_post("/students", get_all_students)

    app.router.add_get("/user/sign-up", user_sign_up_view)
    app.router.add_post("/user/sign-up", user_sign_up)

    app.router.add_get("/administrator/change-info", change_admin_info_view)
    app.router.add_post("/administrator", get_admin)
    app.router.add_post("/administrator/change-info", change_admin_info)

    app.router.add_get("/teacher/change-info", change_teacher_info_view)
    app.router.add_post("/teacher", get_teacher)
    app.router.add_post("/teacher/change-info", change_teacher_info)

    app.router.add_get("/student/change-info", change_student_info_view)
    app.router.add_post("/student", get_student)
    app.router.add_post("/student/change-info", change_student_info)

    app.router.add_get("/student/change-parents-info", change_student_parents_info_view)
    app.router.add_post("/student/parents", get_student_parents)
    app.router.add_post("/student/change-parents-info", change_student_parents_info)

    app.router.add_get("/group/change-info", change_group_info_view)
    app.router.add_post("/group", get_group)
    app.router.add_post("/group/change-info", change_group_info)
