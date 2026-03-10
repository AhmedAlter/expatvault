from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: str | None = None
    nationality: str | None = None
    emirates_id_number: str | None = None
    subscription_tier: str = "free"
    is_active: bool = True
    is_verified: bool = False
    avatar_url: str | None = None
    created_at: str


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=100)
    phone: str | None = None
    nationality: str | None = None
    emirates_id_number: str | None = None
    avatar_url: str | None = None
