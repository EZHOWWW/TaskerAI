from fastapi import APIRouter, Body, status

from .models import UserList
from .services import notification_service

router = APIRouter()


@router.post(
    "/subscribe",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Subscribe users to notifications",
)
async def subscribe_users(payload: UserList = Body(...)):
    """
    Subscribes a list of users to the notification system.
    Fetches their tasks and schedules reminders.
    """
    await notification_service.subscribe(payload.user_ids)
    return {"message": "Subscription process started."}


@router.post(
    "/unsubscribe",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Unsubscribe users from notifications",
)
async def unsubscribe_users(payload: UserList = Body(...)):
    """
    Unsubscribes a list of users and removes all their pending notifications.
    """
    await notification_service.unsubscribe(payload.user_ids)
    return {"message": "Unsubscription process started."}
