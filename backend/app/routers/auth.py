from fastapi import APIRouter, Depends, Request
from supabase import Client
from app.dependencies import get_db, get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    OTPSendRequest,
    OTPVerifyRequest,
    MessageResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=MessageResponse, status_code=201)
def register(body: RegisterRequest, db: Client = Depends(get_db)):
    svc = AuthService(db)
    svc.register(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        phone=body.phone,
        nationality=body.nationality,
    )
    return {"message": "Registration successful. Check your email for verification code."}


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, db: Client = Depends(get_db)):
    svc = AuthService(db)
    device_info = {
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }
    if not body.email and not body.phone:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone required")
    return svc.login(body.email, body.phone, body.password, device_info)


@router.post("/otp/send", response_model=MessageResponse)
def send_otp(body: OTPSendRequest, user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    svc = AuthService(db)
    svc.send_otp(user["id"], user["email"], body.channel)
    return {"message": f"OTP sent via {body.channel}"}


@router.post("/otp/verify", response_model=MessageResponse)
def verify_otp(body: OTPVerifyRequest, user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    svc = AuthService(db)
    svc.verify_otp(user["id"], body.code)
    return {"message": "Email verified successfully"}


@router.post("/token/refresh", response_model=TokenResponse)
def refresh_token(body: RefreshTokenRequest, db: Client = Depends(get_db)):
    svc = AuthService(db)
    return svc.refresh_token(body.refresh_token)


@router.post("/logout", response_model=MessageResponse)
def logout(body: RefreshTokenRequest, db: Client = Depends(get_db)):
    svc = AuthService(db)
    svc.logout(body.refresh_token)
    return {"message": "Logged out successfully"}
