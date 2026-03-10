from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.dependencies import get_db, require_subscription
from app.repositories.family_repo import FamilyRepository
from app.repositories.document_repo import DocumentRepository
from app.schemas.family import FamilyMemberCreateRequest, FamilyMemberUpdateRequest, FamilyMemberResponse
from app.schemas.auth import MessageResponse

router = APIRouter(prefix="/api/v1/family", tags=["family"])

MAX_FAMILY_MEMBERS = 5


@router.get("/members", response_model=list[FamilyMemberResponse])
def list_members(user: dict = Depends(require_subscription("family")), db: Client = Depends(get_db)):
    repo = FamilyRepository(db)
    return repo.list_for_user(user["id"])


@router.post("/members", response_model=FamilyMemberResponse, status_code=201)
def add_member(
    body: FamilyMemberCreateRequest,
    user: dict = Depends(require_subscription("family")),
    db: Client = Depends(get_db),
):
    repo = FamilyRepository(db)
    count = repo.count_for_user(user["id"])
    if count >= MAX_FAMILY_MEMBERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Maximum {MAX_FAMILY_MEMBERS} family members allowed",
        )
    return repo.create({
        "user_id": user["id"],
        "full_name": body.full_name,
        "relationship": body.relationship,
        "date_of_birth": str(body.date_of_birth) if body.date_of_birth else None,
        "nationality": body.nationality,
        "emirates_id_number": body.emirates_id_number,
    })


@router.get("/members/{member_id}", response_model=FamilyMemberResponse)
def get_member(member_id: str, user: dict = Depends(require_subscription("family")), db: Client = Depends(get_db)):
    repo = FamilyRepository(db)
    member = repo.get_by_id(member_id, user["id"])
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family member not found")
    return member


@router.patch("/members/{member_id}", response_model=FamilyMemberResponse)
def update_member(
    member_id: str,
    body: FamilyMemberUpdateRequest,
    user: dict = Depends(require_subscription("family")),
    db: Client = Depends(get_db),
):
    repo = FamilyRepository(db)
    data = body.model_dump(exclude_none=True)
    if data.get("date_of_birth"):
        data["date_of_birth"] = str(data["date_of_birth"])
    updated = repo.update(member_id, user["id"], data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family member not found")
    return updated


@router.delete("/members/{member_id}", response_model=MessageResponse)
def delete_member(member_id: str, user: dict = Depends(require_subscription("family")), db: Client = Depends(get_db)):
    repo = FamilyRepository(db)
    member = repo.get_by_id(member_id, user["id"])
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family member not found")
    repo.delete(member_id, user["id"])
    return {"message": "Family member removed"}


@router.get("/members/{member_id}/documents")
def get_member_documents(
    member_id: str,
    user: dict = Depends(require_subscription("family")),
    db: Client = Depends(get_db),
):
    family_repo = FamilyRepository(db)
    member = family_repo.get_by_id(member_id, user["id"])
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family member not found")

    doc_repo = DocumentRepository(db)
    docs, total = doc_repo.list_for_user(user["id"], family_member_id=member_id)
    return {"data": docs, "total": total}
