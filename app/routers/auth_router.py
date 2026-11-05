from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StaffMember
from app.schemas import LoginRequest
from app.auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication / प्रमाणीकरण"])


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = (
        db.query(StaffMember)
        .filter(StaffMember.username == payload.username.strip())
        .first()
    )
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="प्रयोगकर्ता नाम वा पासवर्ड मिलेन (Invalid username or password)",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="यो खाता निष्क्रिय छ (Account is inactive)",
        )

    token = create_access_token({"sub": user.username, "role": user.role, "uid": user.id})
    response.set_cookie(
        key="vidhi_token",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax",
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "role": user.role,
            "designation": user.designation,
            "bar_council_no": user.bar_council_no,
            "phone": user.phone,
            "email": user.email,
        },
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("vidhi_token")
    return {"message": "सफलतापूर्वक लगआउट भयो (Logged out successfully)"}


@router.get("/me")
def get_me(current_user: StaffMember = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "username": current_user.username,
        "role": current_user.role,
        "designation": current_user.designation,
        "bar_council_no": current_user.bar_council_no,
        "specialization": current_user.specialization,
        "phone": current_user.phone,
        "email": current_user.email,
    }
