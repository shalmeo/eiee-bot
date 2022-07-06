import asyncio

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    album_data = dict()

    def __init__(self, latency: int | float = 0.1):
        self.latency = latency

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            return
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)
            data["album"] = self.album_data[message.media_group_id]

            result = await handler(message, data)

            if message.media_group_id:
                self.album_data.pop(message.media_group_id)

            return result
