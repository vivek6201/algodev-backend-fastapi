from typing import Optional, Any
from pydantic import BaseModel

class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: str
    
class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    
class TokenPayload(BaseModel):
    id: int
    email: str
    role: str