from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from supabase import Client
from app.dependencies import get_db, get_current_user, require_verified_user
from app.services.document_service import DocumentService
from app.services.dependency_engine import DependencyEngine
from app.repositories.document_type_repo import DocumentTypeRepository
from app.repositories.document_repo import DocumentRepository
from app.schemas.document import (
    DocumentCreateRequest,
    DocumentUpdateRequest,
    DocumentResponse,
    DocumentTypeResponse,
)
from app.schemas.auth import MessageResponse

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.get("/types", response_model=list[DocumentTypeResponse])
def get_document_types(db: Client = Depends(get_db)):
    svc = DocumentService(db)
    return svc.get_document_types()


@router.get("/expiring")
def get_expiring_documents(
    days: int = Query(default=90, ge=1, le=365),
    user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    svc = DocumentService(db)
    return svc.get_expiring(user["id"], days)


@router.get("/")
def list_documents(
    status: str | None = None,
    document_type_id: int | None = None,
    family_member_id: str | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    svc = DocumentService(db)
    docs, total = svc.list_documents(
        user["id"],
        status=status,
        document_type_id=document_type_id,
        family_member_id=family_member_id,
        search=search,
        page=page,
        per_page=per_page,
    )
    return {"data": docs, "total": total, "page": page, "per_page": per_page}


@router.post("/", response_model=DocumentResponse, status_code=201)
def create_document(
    document_type_id: int = Form(...),
    title: str = Form(...),
    family_member_id: str | None = Form(None),
    issue_date: str | None = Form(None),
    expiry_date: str | None = Form(None),
    file: UploadFile | None = File(None),
    user: dict = Depends(require_verified_user),
    db: Client = Depends(get_db),
):
    svc = DocumentService(db)
    return svc.create_document(
        user_id=user["id"],
        document_type_id=document_type_id,
        title=title,
        file=file,
        family_member_id=family_member_id,
        issue_date=issue_date,
        expiry_date=expiry_date,
        subscription_tier=user.get("subscription_tier", "free"),
    )


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: str, user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    svc = DocumentService(db)
    return svc.get_document(doc_id, user["id"])


@router.patch("/{doc_id}", response_model=DocumentResponse)
def update_document(
    doc_id: str,
    body: DocumentUpdateRequest,
    user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    svc = DocumentService(db)
    return svc.update_document(doc_id, user["id"], body.model_dump(exclude_none=True))


@router.delete("/{doc_id}", response_model=MessageResponse)
def delete_document(doc_id: str, user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    svc = DocumentService(db)
    svc.archive_document(doc_id, user["id"])
    return {"message": "Document archived"}


@router.get("/{doc_id}/dependencies")
def get_dependencies(doc_id: str, user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    doc_svc = DocumentService(db)
    doc = doc_svc.get_document(doc_id, user["id"])

    type_repo = DocumentTypeRepository(db)
    doc_type = type_repo.get_by_id(doc["document_type_id"])
    all_types = type_repo.get_all()

    engine = DependencyEngine(all_types)
    doc_repo = DocumentRepository(db)
    user_docs = doc_repo.get_user_docs_by_type(user["id"])

    return engine.check_prerequisites(doc_type["name"], user_docs)
