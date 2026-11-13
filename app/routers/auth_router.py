from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StaffMember, Tenant
from app.schemas import LoginRequest
from app.auth import verify_password, create_access_token, get_current_user, get_current_tenant_id

router = APIRouter(prefix="/api/auth", tags=["Authentication / प्रमाणीकरण"])


def build_user_tenant_payload(user: StaffMember, active_tenant_id: int, db: Session) -> dict:
    tenant = db.query(Tenant).filter(Tenant.id == active_tenant_id).first()
    if not tenant:
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    return {
        "id": user.id,
        "tenant_id": active_tenant_id,
        "home_tenant_id": user.tenant_id,
        "is_superadmin": bool(user.is_superadmin),
        "full_name": user.full_name,
        "username": user.username,
        "role": user.role,
        "designation": user.designation,
        "bar_council_no": user.bar_council_no,
        "specialization": user.specialization,
        "phone": user.phone,
        "email": user.email,
        "tenant": {
            "id": tenant.id if tenant else active_tenant_id,
            "tenant_code": tenant.tenant_code if tenant else "VIDHI-001",
            "firm_name_en": tenant.firm_name_en if tenant else "Vidhi Law Firm & Legal Consultancy",
            "firm_name_np": tenant.firm_name_np if tenant else "विधि ल फर्म एण्ड लिगल कन्सल्टेन्सी",
            "firm_type": (tenant.firm_subtitle or "Law, Corporate & Audit Firm") if tenant else "Law, Corporate & Audit Firm",
            "pan_vat_no": (tenant.pan_vat_no or "") if tenant else "",
            "address": (tenant.address or "") if tenant else "",
            "phone": (tenant.phone or "") if tenant else "",
            "email": (tenant.email or "") if tenant else "",
            "receipt_prefix": (tenant.receipt_prefix or "RCP") if tenant else "RCP",
            "subscription_plan": (tenant.subscription_plan or "Enterprise") if tenant else "Enterprise",
            "status": (tenant.subscription_status or "Active") if tenant else "Active",
        },
    }


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

    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if tenant and not user.is_superadmin and (not tenant.is_active or tenant.subscription_status == "Suspended"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="तपाईंको फर्मको सदस्यता स्थगित गरिएको छ (Tenant subscription is suspended)",
        )

    token = create_access_token(
        {
            "sub": user.username,
            "role": user.role,
            "uid": user.id,
            "tid": user.tenant_id,
            "sa": bool(user.is_superadmin),
        }
    )
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
        "user": build_user_tenant_payload(user, user.tenant_id, db),
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("vidhi_token")
    return {"message": "सफलतापूर्वक लगआउट भयो (Logged out successfully)"}


@router.get("/me")
def get_me(
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
):
    return build_user_tenant_payload(current_user, tenant_id, db)
