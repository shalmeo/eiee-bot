from contextlib import suppress

from aiogram import F, Router, Bot
from aiogram import types
from aiogram import html
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from arq import ArqRedis
from sqlalchemy.exc import DBAPIError

from app.keyboards.student.inline.current_tasks import get_input_file_kb
from app.keyboards.student.inline.rejected_files import get_rejected_files_kb
from app.keyboards.teacher.default.menu import get_menu_kb
from app.keyboards.teacher.default.work_files import get_work_files_kb
from app.keyboards.teacher.inline.profile import ProfileAction, ProfileCallbackFactory
from app.misc.delete_message import delete_last_message
from app.misc.file_info import get_file_info
from app.misc.media import get_media_groups
from app.misc.tasks import Tasks
from app.misc.text import get_home_task_text, get_home_work_text
from app.services.database.models import HomeWork
from app.services.database.repositories.default import DefaultRepo
from app.services.database.repositories.teacher import TeacherRepo
from app.keyboards.teacher.inline.check_home_task import (
    HomeTaskAction,
    HomeTaskCallbackFactory,
    get_home_task_info_kb,
    get_select_home_tasks_kb,
    get_check_home_work_kb,
    HomeWorkCallbackFactory,
    get_home_work_info_kb,
    HomeWorkAction,
    get_reject_home_work,
    get_reject_msg_kb,
    RejectHomeWorkCallbackFactory,
    RejectHomeWorkAction,
    HomeTaskPageController,
)
from app.keyboards.teacher.inline.groups import (
    GroupAction,
    GroupCallbackFactory,
    get_groups_kb,
)

router = Router()


@router.callback_query(
    ProfileCallbackFactory.filter(F.action == ProfileAction.CHECK_HOMEWORKS)
)
async def on_select_group_to_check_home_works(
    call: types.CallbackQuery, event_from_user: types.User, repo: DefaultRepo
):
    teacher = await repo.get_teacher(event_from_user.id)
    markup = get_groups_kb(teacher.groups, action=GroupAction.CHECK_HOME_WORK)
    await call.message.edit_text(
        text="Выберите группу для проверки Д/З", reply_markup=markup
    )
    await call.answer()


@router.callback_query(
    GroupCallbackFactory.filter(F.action == GroupAction.CHECK_HOME_WORK)
)
async def on_select_home_task(
    call: types.CallbackQuery,
    callback_data: GroupCallbackFactory,
    state: FSMContext,
    teacher_repo: TeacherRepo,
):
    offset = (await state.get_data()).get("offset") or 0
    home_tasks, limit = await teacher_repo.get_home_tasks(
        callback_data.group_uuid, offset
    )
    count = await teacher_repo.get_count_home_tasks(callback_data.group_uuid)
    markup = get_select_home_tasks_kb(
        home_tasks, offset, limit, count, callback_data.group_uuid
    )
    await call.message.edit_text("Выберите домашнее задание", reply_markup=markup)
    await call.answer()

    await state.update_data(group_id=callback_data.group_uuid)


@router.callback_query(HomeTaskCallbackFactory.filter(F.action == HomeTaskAction.INFO))
async def on_home_task_info(
    call: types.CallbackQuery,
    callback_data: HomeTaskCallbackFactory,
    repo: DefaultRepo,
):
    home_task = await repo.get_home_task(callback_data.task_uuid)
    text = get_home_task_text(home_task, home_task.group.teacher.timezone)
    markup = get_home_task_info_kb(home_task.uuid, home_task.group_id)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()


@router.callback_query(
    HomeTaskCallbackFactory.filter(F.action == HomeTaskAction.IN_CHECK)
)
async def on_in_check_home_works(
    call: types.CallbackQuery,
    callback_data: HomeTaskCallbackFactory,
    teacher_repo: TeacherRepo,
):
    hw_in_check = await teacher_repo.get_in_check_home_works(callback_data.task_uuid)
    markup = get_check_home_work_kb(callback_data.task_uuid, hw_in_check)

    text = ["Список непроверенных домашних работ\n\n"]
    if hw_in_check:
        for i, hw in enumerate(hw_in_check, 1):
            text.append(f"{i}. {hw.student.last_name} {hw.student.first_name}\n")
        text.append("\nВыберите ученика")

    await call.message.edit_text("".join(text), reply_markup=markup)

    await call.answer()


@router.callback_query(HomeWorkCallbackFactory.filter(F.action == HomeWorkAction.INFO))
async def on_home_work_info(
    call: types.CallbackQuery,
    callback_data: HomeWorkCallbackFactory,
    state: FSMContext,
    event_from_user: types.User,
    repo: DefaultRepo,
):
    home_work = await repo.get(HomeWork, callback_data.work_uuid)
    teacher = await repo.get_teacher(event_from_user.id)
    text = get_home_work_text(home_work, teacher.timezone)
    markup = get_home_work_info_kb(home_work.uuid, home_work.home_task_id)
    await call.message.edit_text(text, reply_markup=markup)
    await call.answer()

    await state.update_data(work_uuid=home_work.uuid)


@router.callback_query(
    HomeWorkCallbackFactory.filter(F.action == HomeWorkAction.ATTACHED_FILES)
)
async def on_home_work_files(
    call: types.CallbackQuery,
    callback_data: HomeWorkCallbackFactory,
    state: FSMContext,
    bot: Bot,
    teacher_repo: TeacherRepo,
):
    files = await teacher_repo.get_home_work_files(callback_data.work_uuid)
    photo_media_group, document_media_group, voices = get_media_groups(files)

    markup = get_work_files_kb()
    await call.message.answer("Прикрепленные файлы", reply_markup=markup)

    for media_group in (photo_media_group, document_media_group):
        if media_group:
            await bot.send_media_group(call.from_user.id, media_group)

    if voices:
        for v in voices:
            await call.message.answer_voice(v)

    await call.answer()
    await state.set_state("in_check_work")


@router.message(text="Принять Д/З", state="in_check_work")
async def on_accept_home_work(
    message: types.Message, state: FSMContext, teacher_repo: TeacherRepo
):
    data = await state.get_data()

    await teacher_repo.accept_home_work(data["work_uuid"])
    await message.delete()
    await message.answer("Работа успешно одобрена!", reply_markup=get_menu_kb())
    await teacher_repo.session.commit()


@router.message(text="В доработку", state="in_check_work")
async def on_accept_home_work(message: types.Message, state: FSMContext):
    data = await state.get_data()
    markup = get_reject_home_work(data["work_uuid"])
    m = await message.answer(
        "Комментарий к Д/З\n\n"
        "Если желаете оставить комментарий, отправте сюда сообщения или файлы, которые хотите прикрепить",
        reply_markup=markup,
    )

    await state.set_state("input_reject_message")
    await state.update_data(work_uuid=data["work_uuid"], mid=m.message_id, files=[])


@router.message(text="Назад", state="in_check_work")
async def to_back(message: types.Message, state: FSMContext, repo: DefaultRepo):
    data = await state.get_data()

    markup = get_menu_kb()
    await message.answer("Отменено", reply_markup=markup)
    home_work = await repo.get(HomeWork, data["work_uuid"])
    teacher = await repo.get_teacher(message.from_user.id)
    text = get_home_work_text(home_work, teacher.timezone)
    markup = get_home_work_info_kb(home_work.uuid, home_work.home_task_id)
    await message.answer(text, reply_markup=markup)

    await state.clear()
    await state.update_data(work_uuid=home_work.uuid)


@router.callback_query(
    HomeWorkCallbackFactory.filter(F.action == HomeWorkAction.ACCEPT_HW)
)
async def on_accept_home_work(
    call: types.CallbackQuery,
    callback_data: HomeWorkCallbackFactory,
    state: FSMContext,
    teacher_repo: TeacherRepo,
):
    await teacher_repo.accept_home_work(callback_data.work_uuid)
    await call.message.delete()
    await call.message.answer("Работа успешно одобрена!")
    await teacher_repo.session.commit()
    await state.clear()


@router.callback_query(
    HomeWorkCallbackFactory.filter(F.action == HomeWorkAction.REJECT_HW)
)
async def on_reject_home_work(
    call: types.CallbackQuery, callback_data: HomeWorkCallbackFactory, state: FSMContext
):
    markup = get_reject_home_work(callback_data.work_uuid)
    m = await call.message.edit_text(
        "Комментарий к Д/З\n\n"
        "Если желаете оставить комментарий, отправте сюда сообщения или файлы, которые хотите прикрепить",
        reply_markup=markup,
    )
    await call.answer()
    await state.set_state("input_reject_message")
    await state.update_data(
        work_uuid=callback_data.work_uuid, mid=m.message_id, files=[]
    )


@router.message(
    F.photo[-1].as_("photo"),
    F.media_group_id.as_("media_group_id"),
    state="input_reject_message",
)
async def input_reject_album(
    message: types.Message,
    photo: types.PhotoSize,
    media_group_id: str,
    redis: ArqRedis,
    tasks: Tasks,
):
    await redis.zadd(
        f"media_group:{media_group_id}",
        member=f"{photo.file_id}:{message.content_type}",
        score=float(message.message_id),
    )
    await tasks.handle_media_group(
        chat_id=message.chat.id,
        media_group_id=media_group_id,
        callback="attach_reject_files",
    )


@router.message(
    F.media_group_id.as_("media_group_id"),
    content_types=["document"],
    state="input_reject_message",
)
async def input_reject_media_group(
    message: types.Message, media_group_id: str, redis: ArqRedis, tasks: Tasks
):
    file_id = get_file_info(message)

    await redis.zadd(
        f"media_group:{media_group_id}",
        member=f"{file_id}:{message.content_type}",
        score=float(message.message_id),
    )
    await tasks.handle_media_group(
        chat_id=message.chat.id,
        media_group_id=media_group_id,
        callback="attach_reject_files",
    )


@router.message(
    content_types=["document", "voice", "photo"],
    state="input_reject_message",
)
async def on_input_file(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await delete_last_message(bot, message.from_user.id, data.get("mid"))

    files: list = data.get("files")
    file_id = get_file_info(message)
    files.append((file_id, message.content_type))

    markup = get_input_file_kb(callback="attach_reject_files")
    msg = await message.answer(
        f"Отправлено файлов: <code>{len(files)}</code>\n\n"
        "Если количество файлов не соответствует отправленным, попробуйте отправить еще раз по одному файлу",
        reply_markup=markup,
    )

    await state.update_data(mid=msg.message_id, files=files)


@router.callback_query(text="attach_reject_files", state="input_reject_message")
@router.message(state="input_reject_message")
async def on_reject_message(
    event: types.CallbackQuery | types.Message, bot: Bot, state: FSMContext
):
    data = await state.get_data()
    await delete_last_message(bot, event.from_user.id, data["mid"])
    files = data.get("files", [])

    if isinstance(event, types.Message):
        msg = html.quote(event.text)
    else:
        msg = data.get("rej_msg", "Ваше Д/З отклонено.")

    text = [
        "Комментарий к Д/З\n\n",
        f"Прикрепленных файлов: <code>{len(files)}</code>\n",
        "Ваше сообщение:\n",
        f"{msg}",
    ]

    markup = get_reject_msg_kb(data["work_uuid"])

    if isinstance(event, types.Message):
        m = await event.answer("".join(text), reply_markup=markup)
    else:
        m = await event.message.answer("".join(text), reply_markup=markup)

    await state.update_data(mid=m.message_id, rej_msg=msg)


@router.callback_query(
    RejectHomeWorkCallbackFactory.filter(F.action == RejectHomeWorkAction.WITHOUT_MSG),
    state="input_reject_message",
)
async def on_reject_hw_without_msg(
    call: types.CallbackQuery,
    callback_data: RejectHomeWorkCallbackFactory,
    bot: Bot,
    state: FSMContext,
    teacher_repo: TeacherRepo,
):
    await teacher_repo.reject_home_work(callback_data.work_uuid)
    home_work = await teacher_repo.get_home_work(callback_data.work_uuid)
    await call.message.delete()
    await call.message.answer("Работа успешно отклонена", reply_markup=get_menu_kb())
    await teacher_repo.session.commit()

    last_name = home_work.home_task.group.teacher.last_name
    first_name = home_work.home_task.group.teacher.first_name

    await bot.send_message(
        home_work.student.telegram_id,
        f"Сообщение от учителя: Д/З № <code>{home_work.home_task.number}</code>\n\n"
        f"Учитель: <code>{last_name} {first_name}</code>\n"
        f"Группа: <code>{home_work.home_task.group.title}</code>\n\n"
        f"Сообщение:\nВаше Д/З отклонено.",
    )
    await state.clear()


@router.callback_query(
    RejectHomeWorkCallbackFactory.filter(F.action == RejectHomeWorkAction.WITH_MSG)
)
async def on_rej_hw_with_msg(
    call: types.CallbackQuery,
    callback_data: RejectHomeWorkCallbackFactory,
    state: FSMContext,
    bot: Bot,
    teacher_repo: TeacherRepo,
):
    data = await state.get_data()
    await teacher_repo.reject_home_work(callback_data.work_uuid)
    home_work = await teacher_repo.get_home_work(callback_data.work_uuid)

    files = data.get("files", [])

    for f in files:
        fid, ftype = f
        teacher_repo.add_reject_file(home_work.uuid, fid, ftype)

    await teacher_repo.session.commit()

    await call.message.delete()
    await call.message.answer("Работа успешно отклонена", reply_markup=get_menu_kb())

    last_name = home_work.home_task.group.teacher.last_name
    first_name = home_work.home_task.group.teacher.first_name

    markup = get_rejected_files_kb(home_work.uuid)
    await bot.send_message(
        home_work.student.telegram_id,
        f"Сообщение от учителя: Д/З № <code>{home_work.home_task.number}</code>\n\n"
        f"Учитель: <code>{last_name} {first_name}</code>\n"
        f"Группа: <code>{home_work.home_task.group.title}</code>\n\n"
        f"Сообщение:\n{data['rej_msg']}",
        reply_markup=markup,
    )
    await state.clear()


@router.callback_query(
    HomeTaskCallbackFactory.filter(F.action == HomeTaskAction.COMPLETED)
)
async def on_completed_home_works(
    call: types.CallbackQuery,
    callback_data: HomeTaskCallbackFactory,
    teacher_repo: TeacherRepo,
):
    home_works = await teacher_repo.get_completed_home_works(callback_data.task_uuid)
    text = ["Список принятых домашних работ\n\n"]
    for i, hw in enumerate(home_works, 1):
        text.append(f"{i}. {hw.student.last_name} {hw.student.first_name}\n")

    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Назад",
                    callback_data=HomeTaskCallbackFactory(
                        task_uuid=callback_data.task_uuid, action=HomeTaskAction.INFO
                    ).pack(),
                )
            ]
        ]
    )
    await call.message.edit_text("".join(text), reply_markup=markup)
    await call.answer()


@router.callback_query(HomeTaskPageController.filter())
async def page_controller(
    call: types.CallbackQuery,
    callback_data: HomeTaskPageController,
    state: FSMContext,
    teacher_repo: TeacherRepo,
):
    try:
        home_tasks, limit = await teacher_repo.get_home_tasks(
            callback_data.group_uuid, offset=callback_data.offset
        )
    except DBAPIError:
        await call.answer()
        return

    pages = callback_data.count // limit + bool(callback_data.count % limit)
    current_page = callback_data.offset // limit + 1

    if 1 <= current_page <= pages:
        markup = get_select_home_tasks_kb(
            home_tasks,
            callback_data.offset,
            limit,
            callback_data.count,
            callback_data.group_uuid,
        )
        with suppress(TelegramBadRequest):
            await call.message.edit_reply_markup(markup)

        await state.update_data(offset=callback_data.offset)

    await call.answer()
