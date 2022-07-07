from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.orm import sessionmaker

from app.config_reader import Settings
from app.misc.delete_message import delete_last_message
from app.misc.exceptions import RegisterFormValidateError
from app.misc.models import AdminModel, TeacherModel
from app.misc.parse import parse_admin_register_data, parse_teacher_register_data
from app.services.database.models import Administrator, Teacher
from app.services.database.repositories.default import DefaultRepo


# GET /teacher/change-info
async def change_teacher_info_view(_: Request):
    return FileResponse("html/change_teacher.html")


# POST /teacher
async def get_teacher(request: Request):
    data = await request.post()

    config: Settings = request.app["config"]
    session_factory: sessionmaker = request.app["session_factory"]

    try:
        safe_parse_webapp_init_data(config.bot_token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "error": "Unauthorized"}, status=401)

    async with session_factory() as session:
        repo = DefaultRepo(session)
        teacher = await repo.get_teacher_by_id(int(data["id"]))

    if not teacher:
        return json_response({"ok": False, "error": "Not Found"}, status=404)

    return json_response(
        {
            "ok": True,
            "teacher": {
                "id": teacher.id,
                "first_name": teacher.first_name,
                "last_name": teacher.last_name,
                "patronymic": teacher.patronymic,
                "email": teacher.email,
                "user_name": teacher.user_name,
                "tel": teacher.tel,
                "level": teacher.level,
                "description": teacher.description,
                "timezone": teacher.timezone,
                "telegram_id": teacher.telegram_id,
                "access_start": teacher.access_start.strftime(r"%Y-%m-%d"),
                "access_end": teacher.access_end.strftime(r"%Y-%m-%d"),
            },
        }
    )


# POST /teacher/change-info
async def change_teacher_info(request: Request):
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
        teacher_model = parse_teacher_register_data(data)
    except RegisterFormValidateError:
        return json_response({"ok": False, "error": "Validation error"}, status=400)

    async with session_factory() as session:
        repo = DefaultRepo(session)
        teacher = await repo.get_teacher_by_id(int(data["id"]))

        _update_teacher(teacher, teacher_model)
        await session.commit()

    await _send_info(bot, init_data.user.id, data["msgId"])

    return json_response({"ok": True})


async def _send_info(bot: Bot, chat_id: int, mid: int | str) -> None:
    await delete_last_message(bot, chat_id, mid)
    await bot.send_message(chat_id, "Данные успешно изменены")


def _update_teacher(teacher: Teacher, teacher_model: TeacherModel) -> None:
    teacher.id = teacher_model.id
    teacher.last_name = teacher_model.last_name
    teacher.first_name = teacher_model.first_name
    teacher.patronymic = teacher_model.patronymic
    teacher.email = teacher_model.email
    teacher.user_name = teacher_model.user_name
    teacher.tel = teacher_model.tel
    teacher.telegram_id = teacher_model.tg_id
    teacher.level = teacher_model.level
    teacher.description = teacher_model.description
    teacher.timezone = teacher_model.timezone
    teacher.access_end = teacher_model.access_end
    teacher.access_start = teacher_model.access_start
