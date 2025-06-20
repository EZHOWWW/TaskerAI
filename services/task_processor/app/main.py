from fastapi import FastAPI, status
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

# Import our main data model from the shared library
from core_lib.models.task import Task

# --- API Data Models ---

class TaskProcessRequest(BaseModel):
    """Request model for processing a new goal."""
    goal: str = Field(..., description="The user's high-level goal.", min_length=5)
    user_id: int = Field(1, description="The ID of the user submitting the goal.") # Placeholder

class TaskProcessResponse(BaseModel):
    """Response model after processing a goal."""
    message: str
    processed_task: Task

# --- FastAPI Application ---

app = FastAPI(
    title="TaskerAI: Task Processor Service",
    description="This service decomposes high-level goals into actionable tasks using an LLM.",
    version="0.1.0"
)

@app.post(
    "/process",
    response_model=TaskProcessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Process a high-level goal"
)
async def process_task(request: TaskProcessRequest):
    """
    Accepts a high-level goal and begins the decomposition process.

    This is currently a mock endpoint. It returns a pre-defined task structure
    without calling an actual LLM.
    """
    # TODO: Here we will call the LLM service to process the request.goal
    # For now, we return a hardcoded "dummy" Task object.

    dummy_subtask = Task(title="Step 1: Learn how to boil water")

    processed_task = Task(
        title=request.goal,
        description="This is a root task generated from the user's goal.",
        subtasks=[dummy_subtask],
        complexity=0.5,
        priority=0.5,
        created_at=datetime.utcnow()
    )

    return TaskProcessResponse(
        message="Goal processing started. This is a mock response.",
        processed_task=processed_task
    )

@app.get("/health", status_code=status.HTTP_200_OK, summary="Health Check")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}
