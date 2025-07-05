from typing import List

from pydantic import BaseModel, Field


class UserList(BaseModel):
    """Schema for a list of user IDs."""

    user_ids: List[int] = Field(..., min_length=1)
