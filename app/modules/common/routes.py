from fastapi import File, UploadFile
from fastapi.routing import APIRouter

from .controllers.common_controller import CommonController

common_router = APIRouter()
common_controller = CommonController()


@common_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return await common_controller.upload_file(
        file=file.file, content_type=file.content_type, object_name=file.filename
    )


@common_router.get("/get_file/{object_name}")
def get_file(object_name: str):
    return common_controller.get_file(object_name)
