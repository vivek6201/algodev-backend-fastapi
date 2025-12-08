from fastapi.routing import APIRouter

common_router = APIRouter()


@common_router.post("/upload")
def upload_file():
    pass
