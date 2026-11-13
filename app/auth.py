from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import StaffMember, Tenant


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def extract_token_from_request(request: Request) -> Optional[str]:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1].strip()
    cookie_token = request.cookies.get("vidhi_token")
    if cookie_token:
        return cookie_token
    return None


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> StaffMember:
    token = extract_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="कृपया लगइन गर्नुहोस् (Authentication required)",
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = db.query(StaffMember).filter(StaffMember.username == username, StaffMember.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    # Verify Tenant Status (unless SuperAdmin)
    if not user.is_superadmin:
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if tenant and (not tenant.is_active or tenant.subscription_status == "Suspended"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="तपाईंको फर्मको सदस्यता स्थगित छ (Your tenant subscription is suspended)",
            )
    return user


def get_current_tenant_id(
    request: Request,
    current_user: StaffMember = Depends(get_current_user),
) -> int:
    """Resolve active tenant_id strictly from authenticated user (no tenant picker needed on login).
    Only SaaS SuperAdmin may optionally inspect another tenant via X-Tenant-ID header.
    """
    if current_user.is_superadmin:
        override_tid = request.headers.get("X-Tenant-ID")
        if override_tid and override_tid.isdigit():
            return int(override_tid)
    return current_user.tenant_id or 1


def require_superadmin(current_user: StaffMember = Depends(get_current_user)) -> StaffMember:
    if not current_user.is_superadmin and current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SaaS Host SuperAdmin permission required",
        )
    return current_user
