from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from supabase import Client
from app.repositories.user_repo import UserRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.otp_repo import OTPRepository
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.utils.otp import generate_otp, otp_expiry
from app.utils.email import send_otp_email
from app.config import get_settings


class AuthService:
    def __init__(self, db: Client):
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)
        self.otp_repo = OTPRepository(db)

    def register(self, email: str, password: str, full_name: str, phone: str | None = None, nationality: str | None = None) -> dict:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = self.user_repo.create({
            "email": email,
            "password_hash": hash_password(password),
            "full_name": full_name,
            "phone": phone,
            "nationality": nationality,
        })

        self._send_otp(user["id"], email, "email")
        return user

    def login(self, email: str | None, phone: str | None, password: str, device_info: dict | None = None) -> dict:
        user = None
        if email:
            user = self.user_repo.get_by_email(email)
        elif phone:
            user = self.user_repo.get_by_phone(phone)
        if not user or not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.get("is_active"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

        settings = get_settings()
        access_token = create_access_token(user["id"])
        refresh_token = create_refresh_token()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        self.session_repo.create({
            "user_id": user["id"],
            "refresh_token": refresh_token,
            "device_info": device_info or {},
            "expires_at": expires_at.isoformat(),
        })

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    def refresh_token(self, refresh_token: str) -> dict:
        session = self.session_repo.get_by_refresh_token(refresh_token)
        if not session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        if datetime.fromisoformat(session["expires_at"]) < datetime.now(timezone.utc):
            self.session_repo.delete_by_refresh_token(refresh_token)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        # Rotate refresh token
        self.session_repo.delete_by_refresh_token(refresh_token)
        settings = get_settings()
        new_refresh = create_refresh_token()
        new_access = create_access_token(session["user_id"])
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        self.session_repo.create({
            "user_id": session["user_id"],
            "refresh_token": new_refresh,
            "device_info": session.get("device_info", {}),
            "expires_at": expires_at.isoformat(),
        })

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    def logout(self, refresh_token: str) -> None:
        self.session_repo.delete_by_refresh_token(refresh_token)

    def send_otp(self, user_id: str, email: str, channel: str = "email") -> None:
        since = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        count = self.otp_repo.count_recent(user_id, channel, since)
        if count >= 3:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="OTP rate limit exceeded. Try again in 10 minutes.")
        self._send_otp(user_id, email, channel)

    def _send_otp(self, user_id: str, email: str, channel: str) -> None:
        code = generate_otp()
        self.otp_repo.create({
            "user_id": user_id,
            "code": code,
            "channel": channel,
            "expires_at": otp_expiry().isoformat(),
        })
        if channel == "email":
            send_otp_email(email, code)

    def verify_otp(self, user_id: str, code: str, channel: str = "email") -> bool:
        otp = self.otp_repo.get_latest_for_user(user_id, channel)
        if not otp:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No OTP found. Request a new one.")

        if otp["attempts"] >= otp.get("max_attempts", 3):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Max attempts reached. Request a new OTP.")

        if datetime.fromisoformat(otp["expires_at"]) < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired. Request a new one.")

        if otp["code"] != code:
            self.otp_repo.increment_attempts(otp["id"], otp["attempts"])
            remaining = otp.get("max_attempts", 3) - otp["attempts"] - 1
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid OTP. {remaining} attempts remaining.")

        self.otp_repo.mark_verified(otp["id"])
        self.user_repo.update(user_id, {"is_verified": True})
        return True
