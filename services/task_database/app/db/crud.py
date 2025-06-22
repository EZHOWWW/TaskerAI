from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core_lib.models.task import Task as PydanticTask

from .models import Task as DBTask
from .models import pydantic_to_db


async def get_task_by_id(session: AsyncSession, task_id: int) -> DBTask | None:
    """Fetches a task by its ID."""
    result = await session.execute(select(DBTask).filter(DBTask.id == task_id))
    return result.scalars().first()


async def create_task_in_db(
    session: AsyncSession, task: PydanticTask
) -> DBTask:
    """Creates a new task in the database from a Pydantic model."""
    # Convert Pydantic model to a dictionary, excluding unset fields
    task_data = task.model_dump(exclude_unset=True)

    # The 'subtasks' field in Pydantic is for API, not DB storage
    if "subtasks" in task_data:
        del task_data["subtasks"]

    db_task = pydantic_to_db(task_data)
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)  # Refresh to get the ID from the DB
    return db_task
