from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import datetime


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    created_at: datetime


class UserWithKeysResponse(UserResponse):
    api_keys: Dict[str, Optional[str]]


class UpdateAPIKeysRequest(BaseModel):
    runpod: Optional[str] = None
    openai: Optional[str] = None
    civitai: Optional[str] = None
