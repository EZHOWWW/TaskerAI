from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, Field

# The maximum nesting level for a task.
MAX_TASK_LEVEL = 25


class TaskBase(BaseModel):
    """Base Pydantic model with shared fields."""

    title: str = Field(..., min_length=3, max_length=120)
    description: Optional[str] = None
    level: int = Field(default=0, ge=0, le=MAX_TASK_LEVEL)
    complexity: float = Field(default=0.0, ge=0.0, le=1.0)
    priority: float = Field(default=0.0, ge=0.0, le=1.0)
    tags: List[str] = []
    parent_id: Optional[int] = None

    estimated_duration: Optional[timedelta] = None
    start_time_execution: Optional[datetime] = None
    deadline: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Model used for creating a new task. ID is not needed."""

    user_id: int  # user_id is required for creation


class TaskUpdate(BaseModel):
    """Model used for updating a task. All fields are optional."""

    title: Optional[str] = Field(None, min_length=3, max_length=120)
    description: Optional[str] = None
    level: Optional[int] = Field(None, ge=0, le=MAX_TASK_LEVEL)
    complexity: Optional[float] = Field(None, ge=0.0, le=1.0)
    priority: Optional[float] = Field(None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None
    # parent_id can also be updated
    parent_id: Optional[int] = None

    start_time_execution: Optional[datetime] = None
    estimated_duration: Optional[timedelta] = None
    deadline: Optional[datetime] = None


class Task(TaskBase):
    """
    Model used for reading a task from the DB (includes DB-generated fields).
    """

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskWithSubtasks(Task):
    """
    A recursive model to represent a task with its entire subtree of subtasks.
    """

    subtasks: List["TaskWithSubtasks"] = []


TaskWithSubtasks.model_rebuild()


# Also update the request model for the processor
class TaskProcessRequest(BaseModel):
    goal: str = Field(
        ..., description="The user's high-level goal.", min_length=5
    )
    user_id: int
