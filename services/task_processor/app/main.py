import httpx
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# Import our core components
from core_lib.models.task import Task, TaskUpdate

from .core.logging_config import logger
from .core.processor import TaskProcessor
from .llm.chat_model import get_chat_model

# --- Configuration ---
DATABASE_SERVICE_URL = "http://localhost:8100"


# --- API Data Models ---
class TaskProcessRequest(BaseModel):
    task_id: int


# We will now directly return the Task model as the response
# The response_model will be the Task object itself

# --- FastAPI Application & Core Logic ---
app = FastAPI(
    title="TaskerAI: Task Processor Service",
    description="Decomposes high-level goals into actionable tasks.",
    version="0.1.0",
)

# Initialize the processor once at startup
try:
    chat_model = get_chat_model()
    task_processor = TaskProcessor(model=chat_model)
except ValueError as e:
    # This will prevent the app from starting if the API key is missing
    raise RuntimeError(f"Configuration error: {e}") from e


@app.post(
    "/tasks/process",
    response_model=Task,  # We now return the full Task object
    status_code=status.HTTP_200_OK,  # Changed to OK as it's now synchronous
    summary="Process a high-level goal into a structured task",
)
async def process_and_update_task(request: int):
    logger.info(f"Processing task_id: '{request}'")
    # Get task
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{DATABASE_SERVICE_URL}/tasks/{request}"
            )
            response.raise_for_status()
            task = Task.model_validate(response.json())
        except httpx.RequestError as e:
            logger.error(f"Could not connect to database service: {e}")
            raise HTTPException(
                status_code=503, detail="Database service is unavailable."
            )
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Error response from database service: {e.response.text}"
            )
            raise HTTPException(
                status_code=e.response.status_code, detail=e.response.json()
            )
        logger.info(f"Get task: {repr(task)}")
    # Process task in agent
    logger.info(f"Process task: {repr(task)}")
    try:
        processed_task = await task_processor.process_task(task=task)
    except Exception as e:
        # Handle potential errors from the LLM or parsing
        print(f"Error processing task: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process the goal with the language model.",
        )
    # Update in db
    # TODO subtasks
    logger.info(f"Update task {response}")
    update_data_task = TaskUpdate(**processed_task.model_dump())
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"{DATABASE_SERVICE_URL}/tasks/{request}",
                json=processed_task.model_dump(mode="json"),
            )
            response.raise_for_status()
            updated_task = Task.model_validate(response.json())
        except httpx.RequestError as e:
            logger.error(f"Could not connect to database service: {e}")
            raise HTTPException(
                status_code=503, detail="Database service is unavailable."
            )
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Error response from database service: {e.response.text}"
            )
            raise HTTPException(
                status_code=e.response.status_code, detail=e.response.json()
            )
        logger.info(f"Get task: {repr(task)}")
    return updated_task


@app.get("/health", status_code=status.HTTP_200_OK, summary="Health Check")
def health_check():
    return {"status": "ok"}
