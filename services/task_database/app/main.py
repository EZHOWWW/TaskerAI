# in services/task_database/app/main.py
from typing import List, Optional

from core_lib.models.task import Task, TaskCreate, TaskUpdate, TaskWithSubtasks
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from .db import crud
from .db.session import get_db_session, init_db

app = FastAPI(title="TaskerAI: Database Service")


# --- Events ---
@app.on_event("startup")
async def on_startup():
    await init_db()


# --- API Endpoints ---
@app.post("/tasks/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate, session: AsyncSession = Depends(get_db_session)
):
    """Create a new task. ID is handled automatically."""
    return await crud.create_task_in_db(session=session, task=task)


@app.get("/tasks/", response_model=List[Task])
async def read_user_tasks(
    user_id: int, session: AsyncSession = Depends(get_db_session)
):
    """Retrieve all tasks for a specific user."""
    return await crud.get_tasks_by_user(session=session, user_id=user_id)


@app.get("/tasks/unscheduled/", response_model=List[Task])
async def read_unscheduled_tasks(
    user_id: int, session: AsyncSession = Depends(get_db_session)
):
    """Retrieve future or unscheduled tasks for a user."""
    return await crud.get_unscheduled_tasks(session=session, user_id=user_id)


@app.get("/tasks/search_similar/", response_model=List[Task])
async def search_tasks_by_similarity(
    user_id: int = Query(
        ..., description="ID of the user whose tasks to search"
    ),
    query: str = Query(
        ..., description="The search query text for similar tasks"
    ),
    limit: int = Query(
        5, description="Maximum number of similar tasks to return", ge=1, le=100
    ),
    max_distance: Optional[float] = Query(
        None,
        description="Maximum allowed L2 distance for similarity. Tasks with greater distance will be excluded.",
        ge=0,
    ),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Search for tasks semantically similar to the provided query for a specific user,
    with an optional maximum distance filter.
    """
    return await crud.search_similar_tasks(
        session=session,
        user_id=user_id,
        query=query,
        limit=limit,
        max_distance=max_distance,  # Передаем новый параметр
    )


@app.get("/tasks/{task_id}", response_model=TaskWithSubtasks)
async def read_task(
    task_id: int, session: AsyncSession = Depends(get_db_session)
):
    """Retrieve a single task by its ID, including all its subtasks."""
    # We will use the existing get_task_by_id, SQLAlchemy will handle loading
    db_task = await crud.get_task_by_id(session=session, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    # print(repr(db_task), end="\n\n\n\n")
    return db_task


@app.patch("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Partially update a task's attributes."""
    updated_task = await crud.update_task_in_db(
        session=session, task_id=task_id, task_update=task_update
    )
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int, session: AsyncSession = Depends(get_db_session)
):
    """Delete a task by its ID."""
    success = await crud.delete_task_in_db(session=session, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None
