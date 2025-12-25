import asyncio
import json
import os
from typing import Any, Callable, Optional

import redis.asyncio as redis
from redis.exceptions import RedisError


class AsyncRedisClient:
    """
    Async, event-loop-safe Singleton Redis Client
    """

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

            self.client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                password=os.getenv("REDIS_PASSWORD"),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )

            # Optional startup check
            await self.client.ping()

    # -------------------------
    # Core Utilities
    # -------------------------

    async def ping(self) -> bool:
        try:
            return await self.client.ping()
        except RedisError:
            return False

    async def close(self):
        await self.client.close()

    # -------------------------
    # Basic KV
    # -------------------------

    async def get(self, key: str) -> Optional[str]:
        try:
            return await self.client.get(key)
        except RedisError:
            return None

    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None,
        nx: bool = False,
    ) -> bool:
        try:
            return await self.client.set(
                name=key,
                value=value,
                ex=ttl,
                nx=nx,
            )
        except RedisError:
            return False

    async def delete(self, key: str):
        try:
            await self.client.delete(key)
        except RedisError:
            pass

    # -------------------------
    # JSON Helpers
    # -------------------------

    async def get_json(self, key: str) -> Optional[Any]:
        value = await self.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    async def set_json(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        try:
            return await self.set(key, json.dumps(value), ttl)
        except (TypeError, RedisError):
            return False

    # -------------------------
    # Cache Aside Pattern
    # -------------------------

    async def get_or_set(
        self,
        key: str,
        getter: Callable[[], Any],
        ttl: int = 60,
    ) -> Any:
        cached = await self.get_json(key)
        if cached is not None:
            return cached

        data = await getter()
        await self.set_json(key, data, ttl)
        return data


# ✅ Global instance
redis_client = AsyncRedisClient()
