from pydantic import BaseModel, Field
from datetime import datetime


class ReminderCreateRequest(BaseModel):
    document_id: str
    remind_at: datetime
    days_before: int | None = None
    channel: str = Field(default="in_app", pattern="^(in_app|email|sms)$")


class ReminderUpdateRequest(BaseModel):
    remind_at: datetime | None = None
    channel: str | None = None
    status: str | None = None


class ReminderResponse(BaseModel):
    id: str
    document_id: str
    user_id: str
    remind_at: str
    days_before: int | None = None
    channel: str
    status: str
    sent_at: str | None = None
    snoozed_until: str | None = None
    created_at: str


class SnoozeRequest(BaseModel):
    days: int = Field(default=1, ge=1, le=30)
