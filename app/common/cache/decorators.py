import functools
import inspect
from typing import List, Type, TypeVar

from pydantic.type_adapter import TypeAdapter

from app.common.cache.redis import redis_client
from app.common.db.config import logger

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
                    logger.exception("Cache schema mismatch")

            # 2. Database Call
            result = await func(*args, **kwargs)

            # 3. Save to Cache
            if result:
                # Validate and convert to Pydantic model to ensure relationships are loaded
                adapter = TypeAdapter(response_model)
                validated_result = adapter.validate_python(result)

                dynamic_tags = [t.format(**sig.arguments) for t in (tags or [])]
                # Cache the JSON representation
                json_data = adapter.dump_json(validated_result).decode("utf-8")
                await redis_client.set_with_tags(cache_key, json_data, ttl, dynamic_tags)
                return validated_result

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
