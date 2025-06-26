from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core_lib.models.task import TaskCreate, TaskUpdate

from .mappers import pydantic_to_db_task
from .models import Task as DBTask


# --- READ operations ---
async def get_task_by_id(session: AsyncSession, task_id: int) -> DBTask | None:
    """Fetches a task by its ID."""
    return await session.get(DBTask, task_id)


async def get_tasks_by_user(
    session: AsyncSession, user_id: int
) -> List[DBTask]:
    """Fetches all tasks for a specific user."""
    stmt = (
        select(DBTask)
        .where(DBTask.user_id == user_id)
        .order_by(DBTask.created_at.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_unscheduled_tasks(
    session: AsyncSession, user_id: int
) -> List[DBTask]:
    """Fetches future or unscheduled tasks for a user."""
    stmt = (
        select(DBTask)
        .where(
            DBTask.user_id == user_id,
            (DBTask.deadline == None) | (DBTask.deadline > datetime.utcnow()),
        )
        .order_by(DBTask.priority.desc(), DBTask.deadline.asc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# --- CREATE operation ---
async def create_task_in_db(session: AsyncSession, task: TaskCreate) -> DBTask:
    """Creates a new task using the mapper."""
    db_task = pydantic_to_db_task(task)
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task


# --- UPDATE operation ---
async def update_task_in_db(
    session: AsyncSession, task_id: int, task_update: TaskUpdate
) -> DBTask | None:
    """Updates a task's attributes."""
    print("=========================== BEGIN UPDATE")
    db_task = await get_task_by_id(session, task_id)
    if not db_task:
        return None

    # Get update data, excluding unset values
    update_data = task_update.model_dump(exclude_unset=True)
    print("=========================== BEGIN UPDATE")

    for key, value in update_data.items():
        setattr(db_task, key, value)

    print("=========================== BEGIN UPDATE")
    await session.commit()
    await session.refresh(db_task)
    return db_task


# --- DELETE operation ---
async def delete_task_in_db(session: AsyncSession, task_id: int) -> bool:
    """Deletes a task by its ID."""
    db_task = await get_task_by_id(session, task_id)
    if db_task:
        await session.delete(db_task)
        await session.commit()
        return True
    return False


# --- SEARCH (Future) ---
async def search_similar_tasks(
    session: AsyncSession, user_id: int, query_embedding: List[float]
):
    """
    Template for searching for tasks with similar embeddings.
    The actual embedding model is not part of this service.
    """
    # Placeholder for the search logic
    # stmt = select(DBTask).where(DBTask.user_id == user_id).order_by(DBTask.embedding.l2_distance(query_embedding)).limit(5)
    # result = await session.execute(stmt)
    # return result.scalars().all()
    logger.info("Vector search function called (not implemented yet).")
    return []
