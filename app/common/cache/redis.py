import asyncio
import json
from typing import Any, List, TypeVar

import redis.asyncio as redis
from pydantic import BaseModel
from redis.exceptions import RedisError

from app.config.settings import settings

T = TypeVar("T")


class AsyncRedisClient:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def init(self):
        if hasattr(self, "client"):
            return
        async with self._lock:
            if hasattr(self, "client"):
                return
            try:
                self.client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    decode_responses=True,  # Critical for tag manipulation
                    socket_timeout=5,
                )
            except Exception as e:
                print(e)

    def _get_tag_key(self, tag: str) -> str:
        return f"tag:{tag}"

    async def set_with_tags(self, key: str, value: Any, ttl: int = 600, tags: List[str] = []):
        try:
            # Serialize: Handle Pydantic models, lists, or dicts
            if isinstance(value, BaseModel):
                data = value.model_dump_json()
            elif isinstance(value, (list, dict)):
                data = json.dumps(value, default=str)
            else:
                data = str(value)

            async with self.client.pipeline(transaction=True) as pipe:
                pipe.setex(key, ttl, data)
                for tag in tags:
                    t_key = self._get_tag_key(tag)
                    pipe.sadd(t_key, key)
                    pipe.expire(t_key, ttl)  # Tags live slightly longer than keys
                await pipe.execute()
        except RedisError:
            pass

    async def invalidate_tags(self, tags: List[str]):
        try:
            all_keys = set()
            tag_keys = [self._get_tag_key(t) for t in tags]

            # Fetch all keys associated with these tags
            for t_key in tag_keys:
                keys = await self.client.smembers(t_key)
                if keys:
                    all_keys.update(keys)

            if all_keys:
                async with self.client.pipeline(transaction=True) as pipe:
                    pipe.delete(*all_keys)
                    pipe.delete(*tag_keys)
                    await pipe.execute()
        except RedisError:
            pass


redis_client = AsyncRedisClient()
