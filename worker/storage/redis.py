from typing import Any, Dict, Optional, cast

from aiogram import Bot
from aiogram.dispatcher.fsm.storage.base import BaseStorage
from aiogram.dispatcher.fsm.state import State
from aiogram.dispatcher.fsm.storage.redis import (
    KeyBuilder,
    DefaultKeyBuilder,
    StorageKey,
    StateType,
)

from arq import ArqRedis


class ArqRedisStorage(BaseStorage):
    def __init__(
        self, redis: ArqRedis, key_builder: Optional[KeyBuilder] = None
    ) -> None:
        if key_builder is None:
            self.key_builder = DefaultKeyBuilder()

        self.redis = redis

    async def set_state(
        self, bot: Bot, key: StorageKey, state: StateType = None
    ) -> None:
        redis_key = self.key_builder.build(key, "state")
        if state is None:
            await self.redis.delete(redis_key)
        else:
            await self.redis.set(
                redis_key,
                cast(str, state.state if isinstance(state, State) else state),
            )

    async def get_state(self, bot: Bot, key: StorageKey) -> Optional[str]:
        redis_key = self.key_builder.build(key, "state")
        value = await self.redis.get(redis_key)
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return cast(Optional[str], value)

    async def set_data(self, bot: Bot, key: StorageKey, data: Dict[str, Any]) -> None:
        redis_key = self.key_builder.build(key, "data")
        if not data:
            await self.redis.delete(redis_key)
            return
        await self.redis.set(
            redis_key,
            bot.session.json_dumps(data),
        )

    async def get_data(self, bot: Bot, key: StorageKey) -> Dict[str, Any]:
        redis_key = self.key_builder.build(key, "data")
        value = await self.redis.get(redis_key)
        if value is None:
            return {}
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return cast(Dict[str, Any], bot.session.json_loads(value))

    async def update_data(
        self, bot: Bot, key: StorageKey, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await super().update_data(bot, key, data)
    
    async def close(self) -> None:
        await self.redis.close()
