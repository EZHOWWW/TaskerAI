from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field

# Import our core components
from core_lib.models.task import Task
from .llm.chat_model import get_chat_model
from .core.processor import TaskProcessor

# --- API Data Models ---
class TaskProcessRequest(BaseModel):
    goal: str = Field(..., description="The user's high-level goal.", min_length=5)

# We will now directly return the Task model as the response
# The response_model will be the Task object itself

# --- FastAPI Application & Core Logic ---
app = FastAPI(
    title="TaskerAI: Task Processor Service",
    description="Decomposes high-level goals into actionable tasks.",
    version="0.1.0"
)

# Initialize the processor once at startup
try:
    chat_model = get_chat_model()
    task_processor = TaskProcessor(model=chat_model)
except ValueError as e:
    # This will prevent the app from starting if the API key is missing
    raise RuntimeError(f"Configuration error: {e}") from e

@app.post(
    "/process",
    response_model=Task, # We now return the full Task object
    status_code=status.HTTP_200_OK, # Changed to OK as it's now synchronous
    summary="Process a high-level goal into a structured task"
)
async def process_task(request: TaskProcessRequest):
    """
    Accepts a high-level goal and returns a fully decomposed Task object.
    """
    try:
        # Use our processor to get the structured task
        processed_task = await task_processor.process_goal(goal=request.goal)
        # TODO: Here, we would save the processed_task to the database
        return processed_task
    except Exception as e:
        # Handle potential errors from the LLM or parsing
        print(f"Error processing task: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process the goal with the language model."
        )

@app.get("/health", status_code=status.HTTP_200_OK, summary="Health Check")
def health_check():
    return {"status": "ok"}
