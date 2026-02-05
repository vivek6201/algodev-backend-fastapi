from typing import Any, Dict, Generic, List, Optional, TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class SuccessResponse(JSONResponse):
    def __init__(
        self,
        message: str = "Success",
        data: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        content = {"success": True, "message": message}

        if data is not None:
            content["data"] = jsonable_encoder(data)

        if kwargs:
            content.update(kwargs)

        super().__init__(content=content, status_code=status_code, headers=headers)


class ErrorResponse(JSONResponse):
    def __init__(
        self,
        message: str = "Error",
        error: Any = None,
        headers: Optional[Dict[str, str]] = None,
        status_code: int = 400,
        **kwargs,
    ):
        content = {"success": False, "message": message}

        if error is not None:
            content["error"] = jsonable_encoder(error)

        if kwargs:
            content.update(kwargs)

        super().__init__(content=content, status_code=status_code, headers=headers)


class TokenPayload(BaseModel):
    id: int
    email: str
    role: str
    session_id: Optional[str] = None
    exp: Optional[int] = None


class FileResponse(BaseModel):
    url: str
    type: str
    extension: str
    size: int
    id: str


T = TypeVar("T")


class ListResponse(BaseModel, Generic[T]):
    data: List[T]
    total_items: int
    total_pages: int
