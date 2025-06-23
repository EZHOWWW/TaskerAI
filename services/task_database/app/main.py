from typing import List

from app.core.logging_config import logger
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core_lib.models.task import Task as PydanticTask

from .db import crud
from .db.session import get_db_session, init_db

app = FastAPI(
    title="TaskerAI: Database Service",
    description="Provides a data access API for all task-related operations.",
)


# --- Events ---
@app.on_event("startup")
async def on_startup():
    logger.info("Database service is starting up...")
    await init_db()
    logger.info("Database initialized.")


# --- API Endpoints ---
@app.post(
    "/tasks/", response_model=PydanticTask, status_code=status.HTTP_201_CREATED
)
async def create_task(
    task: PydanticTask, session: AsyncSession = Depends(get_db_session)
):
    """Create a new task in the database."""
    db_task = await crud.create_task_in_db(session=session, task=task)
    return PydanticTask.model_validate(db_task)


@app.get("/tasks/{task_id}", response_model=PydanticTask)
async def get_task(
    task_id: int, session: AsyncSession = Depends(get_db_session)
):
    """Retrieve a single task by its ID."""
    db_task = await crud.get_task_by_id(session=session, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return PydanticTask.model_validate(db_task)


@app.get("/tasks/", response_model=List[PydanticTask])
async def get_root_tasks(session: AsyncSession = Depends(get_db_session)):
    """Retrieve all root-level tasks (tasks without a parent)."""
    # Note: We might need a new CRUD function for this
    db_tasks = await crud.get_all_root_tasks(session=session)
    return [PydanticTask.model_validate(task) for task in db_tasks]


# TODO Change(rewrite) task
# TODO Delete task
# TODO Get all user task(by user id) ...
# TODO Get a task that has a similar meaning (vec search)
