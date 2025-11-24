from typing import Dict, Optional, Any
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class SuccessResponse(JSONResponse):
    def __init__(
        self,
        message: str = "Success",
        data: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        # 1. Start with the standard structure
        content = {"success": True, "message": message}

        # 2. Add 'data' if present
        if data is not None:
            content["data"] = data

        # 3. CRITICAL: Add any extra keyword arguments to the JSON content
        # This allows you to pass extra fields like 'meta', 'trace_id', etc.
        if kwargs:
            content.update(kwargs)

        # 4. Initialize the parent JSONResponse with the finalized content
        # Note: We do NOT pass **kwargs here, preventing the TypeError
        super().__init__(content=content, status_code=status_code, headers=headers)


class ErrorResponse(JSONResponse):
    def __init__(
        self,
        message: str = "Error",
        error: Any = None,
        headers: Optional[Dict[str, str]] = None,
        status_code: int = 400,
        **kwargs
    ):
        content = {"success": False, "message": message}

        if error is not None:
            content["error"] = error

        # Merge extra fields into the JSON response body
        if kwargs:
            content.update(kwargs)

        super().__init__(content=content, status_code=status_code, headers=headers)


class TokenPayload(BaseModel):
    id: int
    email: str
    role: str
    exp: Optional[int] = None
