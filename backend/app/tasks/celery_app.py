try:
    from celery import Celery
    from app.config import get_settings

    settings = get_settings()

    celery_app = Celery(
        "expatvault",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Dubai",
        enable_utc=True,
        beat_schedule={
            "check-reminders-hourly": {
                "task": "app.tasks.reminder_tasks.check_pending_reminders",
                "schedule": 3600.0,
            },
        },
    )

    celery_app.autodiscover_tasks(["app.tasks"])
except ImportError:
    celery_app = None
