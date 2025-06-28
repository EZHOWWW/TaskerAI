from core_lib.models.task import TaskCreate

from .embedding import generate_embedding
from .models import Task as DBTask


def pydantic_to_db_task(task: TaskCreate) -> DBTask:
    """
    Converts a Pydantic TaskCreate model to a SQLAlchemy DBTask model.
    This is where future logic like text embedding can be centralized.
    """
    # Create the DB model instance
    # db_instance = DBTask(**task.model_dump())
    embedding = generate_embedding(
        f"{task.title}\n{task.description}\n{task.tags}"
    )

    db_instance = DBTask(
        title=task.title,
        description=task.description,
        complexity=task.complexity,
        priority=task.priority,
        tags=task.tags,
        level=task.level,
        user_id=task.user_id,
        parent_id=task.parent_id,
        embedding=embedding,
        # estimated_duration=task.estimated_duration,
        start_time_execution=task.start_time_execution,
        deadline=task.deadline,
    )

    # Placeholder for future logic

    return db_instance
