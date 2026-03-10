from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, UploadFile
from supabase import Client
from app.repositories.document_repo import DocumentRepository
from app.repositories.document_type_repo import DocumentTypeRepository
from app.repositories.reminder_repo import ReminderRepository
import hashlib
import uuid


REMINDER_INTERVALS = [90, 60, 30, 14, 7, 3, 1]
DOC_LIMIT_FREE = 10


class DocumentService:
    def __init__(self, db: Client):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.type_repo = DocumentTypeRepository(db)
        self.reminder_repo = ReminderRepository(db)

    def list_documents(self, user_id: str, **filters) -> tuple[list[dict], int]:
        return self.doc_repo.list_for_user(user_id, **filters)

    def get_document(self, doc_id: str, user_id: str) -> dict:
        doc = self.doc_repo.get_by_id(doc_id, user_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return doc

    def create_document(
        self,
        user_id: str,
        document_type_id: int,
        title: str,
        file: UploadFile | None = None,
        family_member_id: str | None = None,
        issue_date: str | None = None,
        expiry_date: str | None = None,
        metadata: dict | None = None,
        subscription_tier: str = "free",
    ) -> dict:
        # Check doc limit for free tier
        if subscription_tier == "free":
            count = self.doc_repo.count_for_user(user_id)
            if count >= DOC_LIMIT_FREE:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Free tier limited to {DOC_LIMIT_FREE} documents. Upgrade to Pro.",
                )

        doc_type = self.type_repo.get_by_id(document_type_id)
        if not doc_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document type")

        file_path = None
        file_hash = None
        file_size = None
        mime_type = None

        if file:
            content = file.file.read()
            file.file.seek(0)
            file_hash = hashlib.sha256(content).hexdigest()
            file_size = len(content)
            mime_type = file.content_type

            ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "pdf"
            storage_name = f"{user_id}/{uuid.uuid4().hex}.{ext}"

            self.db.storage.from_("documents").upload(
                path=storage_name,
                file=content,
                file_options={"content-type": mime_type or "application/octet-stream"},
            )
            file_path = storage_name

        # Determine initial status
        doc_status = "active"
        if expiry_date:
            exp = datetime.fromisoformat(expiry_date) if isinstance(expiry_date, str) else datetime.combine(expiry_date, datetime.min.time())
            if exp.date() < datetime.now(timezone.utc).date():
                doc_status = "expired"
            elif (exp.date() - datetime.now(timezone.utc).date()).days <= 30:
                doc_status = "expiring_soon"

        doc = self.doc_repo.create({
            "user_id": user_id,
            "family_member_id": family_member_id,
            "document_type_id": document_type_id,
            "title": title,
            "file_path": file_path,
            "file_hash": file_hash,
            "file_size_bytes": file_size,
            "mime_type": mime_type,
            "issue_date": str(issue_date) if issue_date else None,
            "expiry_date": str(expiry_date) if expiry_date else None,
            "status": doc_status,
            "metadata": metadata or {},
        })

        # Auto-create reminders if expiry_date is set
        if expiry_date:
            self._create_reminders(doc["id"], user_id, str(expiry_date))

        return doc

    def update_document(self, doc_id: str, user_id: str, data: dict) -> dict:
        existing = self.get_document(doc_id, user_id)
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return existing
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        doc = self.doc_repo.update(doc_id, user_id, update_data)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return doc

    def archive_document(self, doc_id: str, user_id: str) -> None:
        self.get_document(doc_id, user_id)
        self.doc_repo.archive(doc_id, user_id)

    def get_expiring(self, user_id: str, days: int = 90) -> list[dict]:
        return self.doc_repo.get_expiring(user_id, days)

    def get_document_types(self) -> list[dict]:
        return self.type_repo.get_all()

    def _create_reminders(self, doc_id: str, user_id: str, expiry_date: str) -> None:
        exp = datetime.fromisoformat(expiry_date)
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        reminders = []
        for days in REMINDER_INTERVALS:
            remind_at = exp - timedelta(days=days)
            if remind_at > now:
                channel = "in_app"
                if days <= 60:
                    channel = "email"
                if days <= 7:
                    channel = "sms"
                reminders.append({
                    "document_id": doc_id,
                    "user_id": user_id,
                    "remind_at": remind_at.isoformat(),
                    "days_before": days,
                    "channel": channel,
                    "status": "pending",
                })
        if reminders:
            self.reminder_repo.create_bulk(reminders)
