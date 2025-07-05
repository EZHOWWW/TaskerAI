from contextlib import asynccontextmanager

from app.api import router as api_router
from app.clients import client as httpx_client
from app.services import scheduler_service
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    scheduler_service.start()
    yield
    # On shutdown
    scheduler_service.shutdown()
    await httpx_client.aclose()


app = FastAPI(
    title="Notification Service",
    description="A microservice for sending task reminders.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/notifications", tags=["Notifications"])


@app.get("/", tags=["Health Check"])
async def root():
    return {"status": "ok"}
