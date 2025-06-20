import pytest
from pydantic import ValidationError
from datetime import datetime, timedelta
from core_lib.models.task import Task, MAX_TASK_LEVEL

def test_task_creation_success():
    """Tests that a Task can be created with valid data."""
    now = datetime.utcnow()
    task = Task(
        title="Plan world domination",
        description="A detailed plan.",
        priority=0.9,
        complexity=0.8,
        estimated_duration=timedelta(days=365),
        created_at=now
    )

    assert task.title == "Plan world domination"
    assert task.priority == 0.9
    assert task.description == "A detailed plan."

def test_task_fails_without_title():
    """Tests that Task creation fails if title is missing."""
    with pytest.raises(ValidationError):
        Task(description="This task has no title")

def test_task_fails_with_invalid_priority():
    """Tests that Task creation fails with priority out of bounds."""
    with pytest.raises(ValidationError) as e:
        Task(title="Do laundry", priority=1.1)

    assert "priority" in str(e.value)

def test_task_with_subtask():
    """Tests that a Task can contain a sub-task."""
    sub_task = Task(title="Step 1: Get a cat")
    main_task = Task(title="World domination", subtasks=[sub_task])

    assert len(main_task.subtasks) == 1
    assert main_task.subtasks[0].title == "Step 1: Get a cat"
