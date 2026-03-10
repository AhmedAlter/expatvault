from fastapi import APIRouter, Depends
from supabase import Client
from app.dependencies import get_db, get_current_user
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_profile(user: dict = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserResponse)
def update_profile(
    body: UserUpdateRequest,
    user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    repo = UserRepository(db)
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        return user
    updated = repo.update(user["id"], update_data)
    return updated or user
