from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    """User data returned from API endpoints."""
    id: int
    email_verified: bool
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OAuthIdentityResponse(BaseModel):
    """OAuth identity data for API responses."""
    provider: str
    provider_sub: str
    provider_email: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
