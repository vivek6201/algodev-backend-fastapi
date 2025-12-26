import functools
import inspect
from typing import List, Type, TypeVar

from pydantic.type_adapter import TypeAdapter

from app.common.cache.redis import redis_client

T = TypeVar("T")


def cached(key_prefix: str, response_model: Type[T], ttl: int = 3600, tags: List[str] = None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Parse arguments for dynamic keys/tags
            sig = inspect.signature(func).bind(*args, **kwargs)
            sig.apply_defaults()
            # Remove 'self' and 'session' from cache key context
            clean_args = {k: v for k, v in sig.arguments.items() if k not in ("self", "session")}

            cache_key = f"{key_prefix}:" + ":".join(map(str, clean_args.values()))

            # 1. Try Cache
            raw = await redis_client.client.get(cache_key)
            if raw:
                try:
                    return TypeAdapter(response_model).validate_json(raw)
                except Exception:
                    pass  # Schema changed? Ignore and re-fetch

            # 2. Database Call
            result = await func(*args, **kwargs)

            # 3. Save to Cache
            if result:
                dynamic_tags = [t.format(**sig.arguments) for t in (tags or [])]
                await redis_client.set_with_tags(cache_key, result, ttl, dynamic_tags)
            return result

        return wrapper

    return decorator


def invalidate_cache(tags: List[str]):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            # Resolve tags like "job_{job_slug}" using arguments
            sig = inspect.signature(func).bind(*args, **kwargs)
            sig.apply_defaults()
            dynamic_tags = [t.format(**sig.arguments) for t in tags]

            await redis_client.invalidate_tags(dynamic_tags)
            return result

        return wrapper

    return decorator
