import logging

logger = logging.getLogger(__name__)

try:
    from app.tasks.celery_app import celery_app

    if celery_app:
        @celery_app.task
        def check_pending_reminders():
            from datetime import datetime, timezone
            from app.database import get_supabase
            from app.repositories.reminder_repo import ReminderRepository
            from app.repositories.notification_repo import NotificationRepository

            db = get_supabase()
            reminder_repo = ReminderRepository(db)
            notif_repo = NotificationRepository(db)

            now = datetime.now(timezone.utc).isoformat()
            pending = reminder_repo.get_pending_due(now)

            for reminder in pending:
                try:
                    doc = reminder.get("documents", {})
                    doc_title = doc.get("title", "Unknown Document")

                    notif_repo.create({
                        "user_id": reminder["user_id"],
                        "reminder_id": reminder["id"],
                        "title": f"Document Expiring: {doc_title}",
                        "body": f"Your {doc_title} expires on {doc.get('expiry_date', 'N/A')}. {reminder.get('days_before', '?')} days remaining.",
                        "channel": reminder["channel"],
                        "is_read": False,
                    })

                    reminder_repo.update(
                        reminder["id"],
                        reminder["user_id"],
                        {"status": "sent", "sent_at": now},
                    )
                    logger.info(f"Sent reminder {reminder['id']} for doc {doc_title}")
                except Exception as e:
                    logger.error(f"Failed to process reminder {reminder['id']}: {e}")
except ImportError:
    pass
