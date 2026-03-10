from pydantic import BaseModel, Field
from datetime import date, datetime


class DocumentTypeResponse(BaseModel):
    id: int
    name: str
    display_name: str
    category: str | None = None
    typical_validity_days: int | None = None
    renewal_url: str | None = None
    renewal_lead_days: int | None = None
    dependency_chain: list | None = None


class DocumentCreateRequest(BaseModel):
    document_type_id: int
    title: str = Field(min_length=1, max_length=200)
    family_member_id: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    metadata: dict | None = None


class DocumentUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    issue_date: date | None = None
    expiry_date: date | None = None
    metadata: dict | None = None
    status: str | None = None


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    family_member_id: str | None = None
    document_type_id: int
    title: str
    file_path: str | None = None
    file_size_bytes: int | None = None
    mime_type: str | None = None
    issue_date: str | None = None
    expiry_date: str | None = None
    status: str
    ocr_text: str | None = None
    ai_classification: str | None = None
    ai_confidence: float | None = None
    metadata: dict | None = None
    is_archived: bool = False
    created_at: str
    updated_at: str | None = None


class DocumentListParams(BaseModel):
    status: str | None = None
    document_type_id: int | None = None
    family_member_id: str | None = None
    search: str | None = None
    page: int = 1
    per_page: int = 20
