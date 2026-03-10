from fastapi import APIRouter, Depends, Query
from supabase import Client
from app.dependencies import get_db, get_current_user
from app.repositories.notification_repo import NotificationRepository
from app.schemas.notification import NotificationResponse, UnreadCountResponse
from app.schemas.auth import MessageResponse

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("/")
def list_notifications(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    repo = NotificationRepository(db)
    items, total = repo.list_for_user(user["id"], page, per_page)
    return {"data": items, "total": total, "page": page, "per_page": per_page}


@router.get("/unread-count", response_model=UnreadCountResponse)
def unread_count(user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    repo = NotificationRepository(db)
    return {"count": repo.unread_count(user["id"])}


@router.patch("/{notif_id}/read", response_model=NotificationResponse)
def mark_read(notif_id: str, user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    from fastapi import HTTPException, status
    repo = NotificationRepository(db)
    n = repo.mark_read(notif_id, user["id"])
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return n


@router.post("/read-all", response_model=MessageResponse)
def mark_all_read(user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    repo = NotificationRepository(db)
    count = repo.mark_all_read(user["id"])
    return {"message": f"Marked {count} notifications as read"}
