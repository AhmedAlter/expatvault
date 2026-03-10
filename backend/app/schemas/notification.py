from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    reminder_id: str | None = None
    title: str
    body: str
    channel: str
    is_read: bool = False
    read_at: str | None = None
    metadata: dict | None = None
    created_at: str


class UnreadCountResponse(BaseModel):
    count: int
