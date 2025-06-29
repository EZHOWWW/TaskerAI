from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """This class is a base for user-related models and includes fields that are common to all users."""  # noqa: E501

    username: str
    email: EmailStr
    created_at: datetime = datetime.now()
    telegram_account: Optional[str] = None


class UserCreate(UserBase):
    """This class includes an additional field for a password, used when creating new users. It also has a method to create a hashed version of the password."""  # noqa: E501

    password: str


class UserUpdate(UserBase):
    """This class includes optional fields for updating user information. It also has a method to update the hashed version of the password if necessary."""  # noqa: E501

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    telegram_account: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    """This class represents a finalized user model as stored in the database. It includes all fields from `UserBase` plus a password hash for secure storage of passwords."""  # noqa: E501

    password_hash: str
