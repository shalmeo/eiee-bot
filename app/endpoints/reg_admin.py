from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_request import Request
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_response import json_response

from app.config_reader import Settings
from app.keyboards.superadmin.inline.registryof_admins import get_admin_info_kb
from app.misc.exceptions import AdminRegisterFormValidateError
from app.misc.models import AdminRegisterForm
from app.misc.validate import validate_admin_register_data


# GET /administrator/reg-form
async def admin_register_view(request: Request):
    return FileResponse('html/reg_admin.html')


# POST /administrator/register
async def admin_register(request: Request):
    data = await request.post()
    config: Settings = request.app['config']
    bot: Bot = request.app['bot']
    
    try:
        init_data = safe_parse_webapp_init_data(config.bot_token, init_data=data['_auth'])
    except ValueError:
        return json_response({'ok': False, 'error': 'Unauthorized'}, status=401)
    
    try:
        form = validate_admin_register_data(data)
    except AdminRegisterFormValidateError:
        return json_response({'ok': False, 'error': 'Validation error'}, status=400)
    
    await _send_info(bot, init_data.user.id, form)
    
    return json_response({'ok': True})


async def _send_info(bot: Bot, user_id: int, form: AdminRegisterForm) -> None:
    text = [
        '<b>Запись успешно добавлена!</b>\n\n',
        '<b>Администратор</b>\n\n',
        f'<b>Фамилия:</b> <code>{form.last_name}</code>\n'
        f'<b>Имя:</b> <code>{form.first_name}</code>\n',
        f'<b>Отчество:</b> <code>{form.patronymic}</code>\n',
        f'<b>Телефон:</b> <code>+7{form.tel}</code>\n',
        f'<b>Почта:</b> <code>{form.email}</code>\n',
        f'<b>Телеграм ID:</b> <code>{form.tg_id}</code>\n',
        f'<b>Имя пользователя:</b> <code>{form.user_name}</code>\n\n',
        f'<b>Уровень подготовки:</b> <code>{form.level}</code>\n' if form.level else '',
        f'<b>Дополнительное описание:</b>\n<code>{form.description}</code>' if form.description else '', 
    ]
    markup = get_admin_info_kb()
    await bot.edit_message_text(''.join(text), user_id, form.msg_id, reply_markup=markup)