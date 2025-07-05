from typing import List, Optional

import httpx

from core_lib.models.task import Task
from core_lib.models.user import User

from .config import settings

# A single, reusable async client instance
client = httpx.AsyncClient()


async def fetch_user_by_id(user_id: int) -> Optional[User]:
    """Fetches user data from the User Service."""
    try:
        response = await client.get(
            f"{settings.USER_SERVICE_URL}/users/{user_id}"
        )
        response.raise_for_status()
        return User(**response.json())
    except httpx.HTTPStatusError:
        return None


async def fetch_unscheduled_tasks(user_id: int) -> List[Task]:
    """Fetches unscheduled tasks from the Task Service."""
    try:
        response = await client.get(
            f"{settings.TASK_SERVICE_URL}/tasks/unscheduled/",
            params={"user_id": user_id},
        )
        response.raise_for_status()
        tasks_data = response.json()
        return [Task(**task) for task in tasks_data]
    except httpx.HTTPStatusError:
        return []


async def update_user_notification_status(
    user_id: int, is_notified: bool
) -> bool:
    """Requests User Service to update the notification status for a user."""
    try:
        # Assuming user service has a PATCH endpoint like this
        response = await client.patch(
            f"{settings.USER_SERVICE_URL}/users/{user_id}",
            json={"is_notified": is_notified},
        )
        response.raise_for_status()
        return True
    except httpx.HTTPStatusError:
        return False
