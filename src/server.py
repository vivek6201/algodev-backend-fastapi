from app.config.settings import settings
import uvicorn

def main():
    uvicorn.run(
        "app.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )

if __name__ == "__main__":
    main()