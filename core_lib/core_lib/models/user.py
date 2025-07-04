from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from .user_shedule import UserShedule


class UserBase(BaseModel):
    """Base Pydantic model for user data."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

    description_for_llm: Optional[str] = None

    shedule: Optional[UserShedule] = None

    tg_username: Optional[str] = Field(None, min_length=5, max_length=32)
    tg_chat_id: Optional[int] = None


class UserCreate(UserBase):
    """Pydantic model for creating a new user (includes plain password)."""

    password: str = Field(
        ..., min_length=8
    )  # Password should be hashed before saving


class UserUpdate(BaseModel):
    """Pydantic model for updating user data. All fields are optional for partial updates."""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(
        None, min_length=8
    )  # For updating password, will be hashed
    description_for_llm: Optional[str] = None

    shedule: Optional[UserShedule] = None

    tg_username: Optional[str] = Field(None, min_length=5, max_length=32)
    tg_chat_id: Optional[int] = None


class User(UserBase):
    """Full Pydantic model for user data for API responses.
    Can be extended with more fields if needed for API presentation.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = (
            True  # Allows Pydantic to create model from SQLAlchemy objects
        )
