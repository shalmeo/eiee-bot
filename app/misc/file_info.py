from aiogram.types import Message


def get_file_info(m: Message) -> tuple[str]:
    if m.document:
        return m.document.file_id
    elif m.voice:
        return m.voice.file_id
    elif m.photo:
        return m.photo[-1].file_id