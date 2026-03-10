from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta, timezone
from supabase import Client
from app.dependencies import get_db, get_current_user
from app.repositories.reminder_repo import ReminderRepository
from app.schemas.reminder import ReminderCreateRequest, ReminderUpdateRequest, ReminderResponse, SnoozeRequest
from app.schemas.auth import MessageResponse

router = APIRouter(prefix="/api/v1/reminders", tags=["reminders"])


@router.get("/", response_model=list[ReminderResponse])
def list_reminders(
    status: str | None = None,
    user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    repo = ReminderRepository(db)
    return repo.list_for_user(user["id"], status=status)


@router.post("/", response_model=ReminderResponse, status_code=201)
def create_reminder(
    body: ReminderCreateRequest,
    user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    repo = ReminderRepository(db)
    return repo.create({
        "document_id": body.document_id,
        "user_id": user["id"],
        "remind_at": body.remind_at.isoformat(),
        "days_before": body.days_before,
        "channel": body.channel,
        "status": "pending",
    })


@router.get("/{reminder_id}", response_model=ReminderResponse)
def get_reminder(reminder_id: str, user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    from fastapi import HTTPException, status
    repo = ReminderRepository(db)
    r = repo.get_by_id(reminder_id, user["id"])
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    return r


@router.patch("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(
    reminder_id: str,
    body: ReminderUpdateRequest,
    user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    from fastapi import HTTPException, status
    repo = ReminderRepository(db)
    data = body.model_dump(exclude_none=True)
    if data.get("remind_at"):
        data["remind_at"] = data["remind_at"].isoformat()
    updated = repo.update(reminder_id, user["id"], data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    return updated


@router.delete("/{reminder_id}", response_model=MessageResponse)
def delete_reminder(reminder_id: str, user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    repo = ReminderRepository(db)
    repo.delete(reminder_id, user["id"])
    return {"message": "Reminder deleted"}


@router.post("/{reminder_id}/snooze", response_model=ReminderResponse)
def snooze_reminder(
    reminder_id: str,
    body: SnoozeRequest,
    user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    from fastapi import HTTPException, status
    repo = ReminderRepository(db)
    snoozed_until = (datetime.now(timezone.utc) + timedelta(days=body.days)).isoformat()
    updated = repo.update(reminder_id, user["id"], {"status": "snoozed", "snoozed_until": snoozed_until})
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    return updated


@router.post("/{reminder_id}/acknowledge", response_model=ReminderResponse)
def acknowledge_reminder(
    reminder_id: str,
    user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    from fastapi import HTTPException, status
    repo = ReminderRepository(db)
    updated = repo.update(reminder_id, user["id"], {"status": "acknowledged"})
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    return updated
