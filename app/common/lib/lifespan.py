from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.common.cache.redis import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await redis_client.init()
    except Exception as e:
        print(e)

    yield

    try:
        await redis_client.client.close()
    except Exception as e:
        print(e)
