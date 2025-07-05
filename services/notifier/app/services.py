from typing import List

import telegram
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core_lib.models.task import Task

from . import clients
from .config import settings


class TelegramNotifier:
    """Handles sending notifications via Telegram."""

    def __init__(self, token: str):
        self.bot = telegram.Bot(token=token)

    async def send_message(self, chat_id: int, text: str):
        """Sends a message to a given Telegram chat."""
        # This is where LLM agent will be integrated in the future
        message = f"🔔 Напоминание о задаче!\n\n{text}"
        await self.bot.send_message(chat_id=chat_id, text=message)


class SchedulerService:
    """Manages scheduling of notification jobs."""

    def __init__(self, notifier: TelegramNotifier):
        self.scheduler = AsyncIOScheduler()
        self.notifier = notifier

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()

    async def schedule_task_notification(self, task: Task, chat_id: int):
        """Schedules a notification for a single task."""
        job_id = f"task_{task.id}"
        self.scheduler.add_job(
            self.notifier.send_message,
            "date",
            run_date=task.start_time_execution,
            args=[chat_id, task.title],
            id=job_id,
            replace_existing=True,
        )

    def cancel_user_notifications(self, user_id: int):
        """Cancels all scheduled jobs for a user by job_id prefix."""
        # APScheduler doesn't support searching by metadata or partial id directly.
        # We get all jobs and filter them.
        for job in self.scheduler.get_jobs():
            if job.id.startswith(f"user_{user_id}_"):
                try:
                    job.remove()
                except JobLookupError:
                    pass  # Job already ran or was removed


class NotificationService:
    """Orchestrates the notification subscription and delivery logic."""

    def __init__(self, scheduler_service: SchedulerService):
        self.scheduler = scheduler_service

    async def subscribe(self, user_ids: List[int]):
        """Subscribes users to notifications and schedules their tasks."""
        for user_id in user_ids:
            print(f"user {user_id} subscribe")
            user = await clients.fetch_user_by_id(user_id)
            if not user or not user.tg_chat_id:
                continue

            await clients.update_user_notification_status(
                user_id, is_notified=True
            )

            tasks = await clients.fetch_unscheduled_tasks(user_id)
            for task in tasks:
                if task.start_time_execution:
                    await self.scheduler.schedule_task_notification(
                        task, user.tg_chat_id
                    )

    async def unsubscribe(self, user_ids: List[int]):
        """Unsubscribes users and cancels all their scheduled notifications."""
        for user_id in user_ids:
            await clients.update_user_notification_status(
                user_id, is_notified=False
            )
            self.scheduler.cancel_user_notifications(user_id)


# Initialize services
notifier = TelegramNotifier(token=settings.TELEGRAM_BOT_TOKEN)
scheduler_service = SchedulerService(notifier=notifier)
notification_service = NotificationService(scheduler_service=scheduler_service)
