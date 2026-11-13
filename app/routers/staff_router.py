from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StaffMember, LegalCase
from app.schemas import StaffMemberCreate, StaffMemberUpdate
from app.auth import get_current_user, get_current_tenant_id, hash_password

router = APIRouter(prefix="/api/staff", tags=["Advocates & Staff / वकिल तथा कर्मचारी विवरण"])


def serialize_staff(member: StaffMember, db: Session) -> dict:
    lead_count = (
        db.query(LegalCase)
        .filter(LegalCase.tenant_id == member.tenant_id, LegalCase.advocate_id == member.id)
        .count()
    )
    assist_count = (
        db.query(LegalCase)
        .filter(LegalCase.tenant_id == member.tenant_id, LegalCase.assistant_id == member.id)
        .count()
    )
    return {
        "id": member.id,
        "tenant_id": member.tenant_id,
        "full_name": member.full_name,
        "role": member.role,
        "designation": member.designation,
        "bar_council_no": member.bar_council_no or "",
        "specialization": member.specialization or "",
        "phone": member.phone,
        "alt_phone": member.alt_phone or "",
        "email": member.email or "",
        "address": member.address or "",
        "username": member.username,
        "is_active": member.is_active,
        "notes": member.notes or "",
        "lead_cases_count": lead_count,
        "assisted_cases_count": assist_count,
        "total_cases_count": lead_count + assist_count,
        "created_at": member.created_at.isoformat() if member.created_at else None,
    }


@router.get("")
def list_staff(
    role: Optional[str] = Query(None, description="Filter by role: admin, advocate, staff"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    query = db.query(StaffMember).filter(StaffMember.tenant_id == tenant_id)
    if role:
        if role == "advocate":
            query = query.filter(StaffMember.role.in_(["advocate", "admin"]))
        else:
            query = query.filter(StaffMember.role == role)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                StaffMember.full_name.ilike(term),
                StaffMember.phone.ilike(term),
                StaffMember.bar_council_no.ilike(term),
                StaffMember.designation.ilike(term),
                StaffMember.specialization.ilike(term),
            )
        )
    members = query.order_by(StaffMember.id.asc()).all()
    return [serialize_staff(m, db) for m in members]


@router.post("")
def create_staff(
    payload: StaffMemberCreate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    existing = db.query(StaffMember).filter(StaffMember.username == payload.username.strip()).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="यो प्रयोगकर्ता नाम (username) पहिले नै दर्ता छ (Username already taken across platform)",
        )

    member = StaffMember(
        tenant_id=tenant_id,
        full_name=payload.full_name.strip(),
        role=payload.role,
        designation=payload.designation,
        bar_council_no=payload.bar_council_no,
        specialization=payload.specialization,
        phone=payload.phone.strip(),
        alt_phone=payload.alt_phone,
        email=payload.email.strip() if payload.email else None,
        address=payload.address,
        username=payload.username.strip(),
        password_hash=hash_password(payload.password),
        is_active=payload.is_active,
        notes=payload.notes,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return serialize_staff(member, db)


@router.put("/{staff_id}")
def update_staff(
    staff_id: int,
    payload: StaffMemberUpdate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    member = (
        db.query(StaffMember)
        .filter(StaffMember.id == staff_id, StaffMember.tenant_id == tenant_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="वकिल वा कर्मचारी भेटिएन")

    update_data = payload.model_dump(exclude_unset=True)
    if "password" in update_data:
        raw_pw = update_data.pop("password")
        if raw_pw and len(raw_pw.strip()) >= 4:
            member.password_hash = hash_password(raw_pw.strip())

    for key, val in update_data.items():
        if key == "email" and not val:
            val = None
        setattr(member, key, val)

    db.commit()
    db.refresh(member)
    return serialize_staff(member, db)


@router.delete("/{staff_id}")
def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    member = (
        db.query(StaffMember)
        .filter(StaffMember.id == staff_id, StaffMember.tenant_id == tenant_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="वकिल वा कर्मचारी भेटिएन")
    if member.id == current_user.id:
        raise HTTPException(status_code=400, detail="आफ्नै सक्रिय खाता हटाउन मिल्दैन")

    db.delete(member)
    db.commit()
    return {"message": "विवरण हटाइयो"}
