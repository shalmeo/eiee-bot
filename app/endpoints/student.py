from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from app.config_reader import Settings
from app.misc.delete_message import delete_last_message
from app.misc.exceptions import RegisterFormValidateError
from app.misc.models import StudentModel
from app.misc.parse import (
    parse_student_register_data,
)
from app.services.database.models import Student
from app.services.database.repositories.default import DefaultRepo


# GET /student/change-info
async def change_student_info_view(_: Request):
    return FileResponse("html/change_student.html")


# POST /student
async def get_student(request: Request):
    data = await request.post()

    config: Settings = request.app["config"]
    session_factory: sessionmaker = request.app["session_factory"]

    try:
        safe_parse_webapp_init_data(config.bot_token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    async with session_factory() as session:
        repo = DefaultRepo(session)
        student = await repo.get_student_by_id(int(data["id"]))

    if not student:
        return json_response({"ok": False, "error": "Not Found"}, status=404)

    return json_response(
        {
            "ok": True,
            "student": {
                "id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "patronymic": student.patronymic,
                "email": student.email,
                "user_name": student.user_name,
                "tel": student.tel,
                "timezone": student.timezone,
                "telegram_id": student.telegram_id,
                "access_start": student.access_start.strftime(r"%Y-%m-%d"),
                "access_end": student.access_end.strftime(r"%Y-%m-%d"),
            },
        }
    )


# POST /student/change-info
async def change_student_info(request: Request):
    data = await request.post()

    config: Settings = request.app["config"]
    session_factory: sessionmaker = request.app["session_factory"]
    bot: Bot = request.app["bot"]

    try:
        init_data = safe_parse_webapp_init_data(
            config.bot_token, init_data=data["_auth"]
        )
    except ValueError:
        return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    try:
        student_model = parse_student_register_data(data)
    except RegisterFormValidateError:
        return json_response({"ok": False, "error": "Validation error"}, status=400)

    async with session_factory() as session:
        repo = DefaultRepo(session)
        student = await repo.get_student_by_id(int(data["id"]))

        _update_student(student, student_model)
        await session.commit()

    await _send_info(bot, init_data.user.id, data["msgId"])

    return json_response({"ok": True})


async def _send_info(bot: Bot, chat_id: int, mid: int | str) -> None:
    await delete_last_message(bot, chat_id, mid)
    await bot.send_message(chat_id, "Данные успешно изменены")


def _update_student(student: Student, student_model: StudentModel) -> None:
    student.id = student_model.id
    student.last_name = student_model.last_name
    student.first_name = student_model.first_name
    student.patronymic = student_model.patronymic
    student.email = student_model.email
    student.user_name = student_model.user_name
    student.tel = student_model.tel
    student.telegram_id = student_model.tg_id
    student.timezone = student_model.timezone
    student.access_end = student_model.access_end
    student.access_start = student_model.access_start
