from datetime import datetime
from typing import List, Optional

from core_lib.models.task import TaskCreate, TaskUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .embedding import generate_embedding
from .mappers import pydantic_to_db_task
from .models import Task as DBTask

EMBEDDING_DIMENSION = 384
ZERO_EMBEDDING = [0.0] * EMBEDDING_DIMENSION


# --- READ operations ---
async def get_task_by_id(session: AsyncSession, task_id: int) -> DBTask | None:
    """
    Fetches a task by its ID and eagerly loads the entire subtask tree
    to prevent lazy loading issues in an async context.
    """
    # This strategy tells SQLAlchemy to load the 'subtasks' relationship,
    # and for each of those subtasks, to also load their 'subtasks', and so on.
    # We can chain this to handle multiple levels of nesting.
    # For a reasonably deep tree (e.g., up to 5 levels), this is effective.
    recursive_load = selectinload(DBTask.subtasks)
    for _ in range(4):  # Loop 4 times for a total depth of 5 levels
        recursive_load = recursive_load.selectinload(DBTask.subtasks)

    # We build the query explicitly
    stmt = select(DBTask).where(DBTask.id == task_id).options(recursive_load)

    result = await session.execute(stmt)
    # scalar_one_or_none() correctly assembles the single result object
    return result.scalar_one_or_none()


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
    db_task = await get_task_by_id(session, task_id)
    if not db_task:
        return None

    # Get update data, excluding unset values
    update_data = task_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    await session.commit()
    await session.refresh(db_task)
    await session.refresh(db_task, attribute_names=["parent", "subtasks"])
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
    session: AsyncSession,
    user_id: int,
    query: str,
    limit: int = 5,
    max_distance: Optional[float] = None,
) -> List[DBTask]:
    """
    Searches for tasks with similar embeddings based on a given query string,
    with an optional maximum distance constraint.

    Args:
        session (AsyncSession): The SQLAlchemy async session.
        user_id (int): The ID of the user whose tasks to search.
        query (str): The search query string.
        limit (int): The maximum number of similar tasks to return.
        max_distance (Optional[float]): The maximum L2 distance allowed for a task to be considered similar.
                                       If None, no distance constraint is applied.

    Returns:
        List[DBTask]: A list of similar tasks, ordered by similarity and within the distance constraint.
    """
    query_embedding = generate_embedding(query)

    # Вычисляем расстояние и используем его для фильтрации
    distance_column = DBTask.embedding.l2_distance(query_embedding)

    stmt = select(DBTask).where(
        DBTask.user_id == user_id,
        DBTask.embedding.l2_distance(ZERO_EMBEDDING) > 0,
    )

    if max_distance is not None:
        stmt = stmt.where(distance_column <= max_distance)

    stmt = stmt.order_by(distance_column).limit(limit)

    result = await session.execute(stmt)
    return result.scalars().all()
