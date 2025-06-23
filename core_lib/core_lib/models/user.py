from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """
    Main user class model.
    """

    id: Optional[int] = None

    name: str = Field(..., min_length=3, max_length=128)

    # a more detailed description of the task, optional
    email: Optional[str] = None

    pswd_hash: Optional[EmailStr] = None

    # TODO

    class Config:
        from_attributes = True
