from pydantic import BaseModel, model_validator, EmailStr, field_validator
from typing import Optional

class Login(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str
    
    @model_validator(mode='after')
    def validate_info(self):
        if not self.email and not self.username:
            raise ValueError('Either email or username must be provided')
        if self.email and self.username:
            raise ValueError('Provide either email or username, not both')
        return self
    
class Signup(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    
    @field_validator('password')
    def password_length(cls, v):
        if not (6 <= len(v) <= 16):
            raise ValueError("Password must be between 6 and 16 characters.")
        return v
