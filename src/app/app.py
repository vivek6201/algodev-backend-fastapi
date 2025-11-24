from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from app.router import router
from app.config.settings import settings
import logging
from app.common.lib.exception_handlers import validation_exception_handler,general_exception_handler 
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.modules.users.models.user import Users
from app.modules.jobs.models.jobs import Job, Category, JobCategoryLink, Company, JobApplication  

app = FastAPI(
    title=settings.PROJECT_NAME,    
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(StarletteHTTPException, general_exception_handler)


if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts = settings.ALLOWED_HOSTS
    )

app.include_router(router, prefix="/api")
