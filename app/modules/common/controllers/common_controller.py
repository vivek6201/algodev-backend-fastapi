import os
import uuid
from typing import IO

from fastapi import HTTPException

from app.common.lib.formatter import SuccessResponse

from ..services.s3_service import S3Service


class CommonController:
    def __init__(self):
        self.s3_service = S3Service()

    async def upload_file(self, file: IO, object_name: str, content_type: str = None):
        try:
            # Generate unique filename to prevent overwrite
            _, file_extension = os.path.splitext(object_name)
            unique_key = f"{uuid.uuid4()}{file_extension}"

            key = await self.s3_service.upload_file(file, unique_key, content_type)
            if not key:
                raise HTTPException(status_code=500, detail="Failed to upload file")

            return SuccessResponse(data={"key": key}, message="File uploaded successfully")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_file(self, object_name: str):
        try:
            url = self.s3_service.get_url(object_name)
            if not url:
                raise HTTPException(status_code=500, detail="Failed to generate signed URL")

            return SuccessResponse(data={"url": url}, message="File URL generated successfully")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
