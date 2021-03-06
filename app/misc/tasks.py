import datetime
from datetime import timedelta

from arq import ArqRedis
from arq.jobs import Job


class Tasks:
    def __init__(self, redis: ArqRedis):
        self.redis = redis

    async def handle_media_group(
        self, chat_id: int, media_group_id: str, callback: str
    ) -> Job:
        return await self.redis.enqueue_job(
            "handle_media_group_task",
            chat_id=chat_id,
            media_group_id=media_group_id,
            callback=callback,
            _defer_by=timedelta(seconds=1),
            _job_id=f"media_group:{media_group_id}",
        )

    async def send_message(
        self, chat_id: int, text: str, dt: datetime.datetime = None
    ) -> Job:
        if dt:
            return await self.redis.enqueue_job(
                "send_message_task", chat_id=chat_id, text=text, _defer_until=dt
            )

        return await self.redis.enqueue_job(
            "send_message_task", chat_id=chat_id, text=text
        )
