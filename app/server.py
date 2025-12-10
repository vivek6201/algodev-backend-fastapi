import uvicorn

from app.config.settings import settings


def main():
    uvicorn.run(
        "app.app:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level="debug" if settings.DEBUG else "info",
    )


def dev():
    uvicorn.run(
        "app.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="debug",
    )


if __name__ == "__main__":
    main()
