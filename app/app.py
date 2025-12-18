import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.lib.exception_handlers import (
    general_exception_handler,
    validation_exception_handler,
)
from app.config.router import router
from app.config.settings import settings

# importing models for alembic
from app.modules.education.blogs.models.blog import *  # noqa: F403
from app.modules.education.shared.model import *  # noqa: F403
from app.modules.jobs.models.jobs import *  # noqa: F403
from app.modules.users.models.admin import *  # noqa: F403
from app.modules.users.models.user import *  # noqa: F403

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(StarletteHTTPException, general_exception_handler)


if not settings.DEBUG:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.TRUSTED_HOSTS)

app.include_router(router, prefix="/api")
