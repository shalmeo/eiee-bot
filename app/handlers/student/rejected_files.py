from aiogram import Router, types, Bot

from app.keyboards.student.inline.rejected_files import RejectedFilesCallbackFactory
from app.misc.media import get_media_groups
from app.services.database.repositories.student import StudentRepo

router = Router()


@router.callback_query(RejectedFilesCallbackFactory.filter(), state="*")
async def show_rejected_files(
    call: types.CallbackQuery,
    callback_data: RejectedFilesCallbackFactory,
    bot: Bot,
    student_repo: StudentRepo,
):
    files = await student_repo.get_rejected_files(callback_data.work_uuid)
    photo_media_group, document_media_group, voices = get_media_groups(files)

    for media_group in (photo_media_group, document_media_group):
        if media_group:
            await bot.send_media_group(call.from_user.id, media_group)

    if voices:
        for v in voices:
            await call.message.answer_voice(v)

    await call.answer()
