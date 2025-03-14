from dataclasses import dataclass, field
from datetime import datetime

NOW = datetime(1, 1, 1, 0, 0, 0)


@dataclass
class DateTimeTask:
    date_set_task: datetime = NOW
    date_start_task: datetime = NOW
    time_to_do_task: datetime = NOW
    deadline: datetime = NOW


@dataclass
class Task:
    text: str = "Empty task"
    lvl: int = 0
    tags: list = field(default_factory=list)
    complexity: float = 0.0
    priority: float = 0.0
    date_time_task: DateTimeTask = field(default_factory=DateTimeTask)
    subtasks: list = field(default_factory=list)
