from core_lib.models.task import TaskCreate

from .models import Task as DBTask


def pydantic_to_db_task(task: TaskCreate) -> DBTask:
    """
    Converts a Pydantic TaskCreate model to a SQLAlchemy DBTask model.
    This is where future logic like text embedding can be centralized.
    """
    # Create the DB model instance
    # db_instance = DBTask(**task.model_dump())
    db_instance = DBTask(
        title=task.title,
        description=task.description,
        complexity=task.complexity,
        priority=task.priority,
        tags=task.tags,
        level=task.level,
        user_id=task.user_id,
    )

    # Placeholder for future logic
    # if task.title:
    #     db_instance.embedding = generate_embedding(task.title) # Example

    return db_instance
