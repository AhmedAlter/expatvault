from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from app.database import get_supabase
from app.utils.security import decode_access_token
from app.repositories.user_repo import UserRepository

security = HTTPBearer()


def get_db() -> Client:
    return get_supabase()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_db),
) -> dict:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(payload["sub"])
    if not user or not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


def require_verified_user(user: dict = Depends(get_current_user)) -> dict:
    if not user.get("is_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )
    return user


def require_subscription(tier: str):
    tier_levels = {"free": 0, "individual_pro": 1, "family": 2}

    def checker(user: dict = Depends(require_verified_user)) -> dict:
        user_level = tier_levels.get(user.get("subscription_tier", "free"), 0)
        required_level = tier_levels.get(tier, 0)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription tier '{tier}' or higher required",
            )
        return user

    return checker
