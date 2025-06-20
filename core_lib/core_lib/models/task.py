from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional, List, Self

# The maximum nesting level for a task.
MAX_TASK_LEVEL = 25

class Task(BaseModel):
    """
    Represents a single task, which can be a main goal or a sub-task.
    """
    id: Optional[int] = None

    # a short, clear title for the task
    title: str = Field(..., min_length=3, max_length=120)

    # a more detailed description of the task, optional
    description: Optional[str] = None

    # a list of sub-tasks for decomposition
    subtasks: List[Self] = []

    # level of task nesting, validated against the global max
    level: int = Field(default=0, ge=0, le=MAX_TASK_LEVEL)

    # tags for categorization
    tags: List[str] = []

    # estimated complexity from 0.0 to 1.0
    complexity: float = Field(default=0.0, ge=0.0, le=1.0)

    # priority from 0.0 to 1.0
    priority: float = Field(default=0.0, ge=0.0, le=1.0)

    # estimated time required to complete the task
    estimated_duration: Optional[timedelta] = None

    # the deadline for the task
    deadline: Optional[datetime] = None

    # timestamp of when the task was created
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
