from typing import Iterable

from aiogram import types

from app.services.database.models import HomeTaskFile, HomeWorkFile


def get_media_groups(files: Iterable[HomeTaskFile | HomeWorkFile]):
    photo_media_group = list()
    document_media_group = list()
    voices = list()
    for file in files:
        if file.type == types.ContentType.VOICE:
            voices.append(file.id)
        else:
            (
                photo_media_group.append(types.InputMediaPhoto(media=file.id))
                if file.type == types.ContentType.PHOTO
                else document_media_group.append(
                    types.InputMediaDocument(media=file.id)
                )
            )

    return photo_media_group, document_media_group, voices
