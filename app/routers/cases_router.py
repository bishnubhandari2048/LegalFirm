from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LegalCase, Client, StaffMember, PaymentRecord, Hearing, CaseDocument, Tenant
from app.schemas import LegalCaseCreate, LegalCaseUpdate
from app.auth import get_current_user, get_current_tenant_id
from app.bs_calendar import bs_to_ad, ad_to_bs, format_bs_human

router = APIRouter(prefix="/api/cases", tags=["Cases / मुद्दाको विवरण"])


def recalculate_case_financials(legal_case: LegalCase, db: Session):
    total_paid = sum(p.amount for p in (legal_case.payments or []))
    legal_case.paid_amount = round(total_paid, 2)
    legal_case.due_amount = round(max(0.0, (legal_case.deal_amount or 0.0) - total_paid), 2)


def serialize_case(c: LegalCase, include_details: bool = False) -> dict:
    data = {
        "id": c.id,
        "tenant_id": c.tenant_id,
        "case_number": c.case_number,
        "filing_number": c.filing_number or "",
        "case_title": c.case_title or f"{c.client.full_name if c.client else ''} वि. {c.opponent_name}",
        "court_name": c.court_name,
        "bench_section": c.bench_section or "",
        "case_type": c.case_type,
        "client_id": c.client_id,
        "client_name": c.client.full_name if c.client else "",
        "client_phone": c.client.phone if c.client else "",
        "client_citizenship": c.client.citizenship_no if c.client else "",
        "client_address": c.client.address if c.client else "",
        "client_party_role": c.client_party_role,
        "opponent_name": c.opponent_name,
        "opponent_address": c.opponent_address or "",
        "opponent_contact": c.opponent_contact or "",
        "opponent_counsel": c.opponent_counsel or "",
        "registration_date_bs": c.registration_date_bs,
        "registration_date_bs_human": format_bs_human(c.registration_date_bs),
        "registration_date_ad": c.registration_date_ad.isoformat() if c.registration_date_ad else "",
        "status": c.status,
        "deal_amount": round(c.deal_amount or 0.0, 2),
        "paid_amount": round(c.paid_amount or 0.0, 2),
        "due_amount": round(c.due_amount or 0.0, 2),
        "advocate_id": c.advocate_id,
        "advocate_name": c.advocate.full_name if c.advocate else "तोकिएको छैन",
        "advocate_phone": c.advocate.phone if c.advocate else "",
        "advocate_bar_no": c.advocate.bar_council_no if c.advocate else "",
        "assistant_id": c.assistant_id,
        "assistant_name": c.assistant.full_name if c.assistant else "तोकिएको छैन",
        "assistant_phone": c.assistant.phone if c.assistant else "",
        "waris_name": c.waris_name or "",
        "next_hearing_date_bs": c.next_hearing_date_bs or "",
        "next_hearing_date_bs_human": format_bs_human(c.next_hearing_date_bs) if c.next_hearing_date_bs else "-",
        "next_hearing_date_ad": c.next_hearing_date_ad.isoformat() if c.next_hearing_date_ad else "",
        "summary": c.summary or "",
        "hearings_count": len(c.hearings or []),
        "documents_count": len(c.documents or []),
        "payments_count": len(c.payments or []),
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
    if include_details:
        data["hearings"] = [
            {
                "id": h.id,
                "hearing_date_bs": h.hearing_date_bs,
                "hearing_date_ad": h.hearing_date_ad.isoformat() if h.hearing_date_ad else "",
                "hearing_status": h.hearing_status,
                "bench_or_judge": h.bench_or_judge or "",
                "next_hearing_date_bs": h.next_hearing_date_bs or "",
                "outcome": h.outcome or "",
                "attended_by_name": h.attended_by.full_name if h.attended_by else "",
                "remarks": h.remarks or "",
            }
            for h in (c.hearings or [])
        ]
        data["payments"] = [
            {
                "id": p.id,
                "amount": p.amount,
                "payment_date_bs": p.payment_date_bs,
                "payment_date_ad": p.payment_date_ad.isoformat() if p.payment_date_ad else "",
                "payment_method": p.payment_method,
                "receipt_number": p.receipt_number,
                "purpose": p.purpose,
                "reference_no": p.reference_no or "",
                "remarks": p.remarks or "",
                "received_by_name": p.received_by.full_name if p.received_by else "",
            }
            for p in (c.payments or [])
        ]
        data["documents"] = [
            {
                "id": d.id,
                "document_name": d.document_name,
                "document_type": d.document_type,
                "status": d.status,
                "received_date_bs": d.received_date_bs,
                "returned_date_bs": d.returned_date_bs or "",
                "handover_person": d.handover_person or "",
                "file_path": d.file_path or "",
                "file_name": d.file_name or "",
                "remarks": d.remarks or "",
            }
            for d in (c.documents or [])
        ]
    return data


@router.get("")
def list_cases(
    search: Optional[str] = Query(None),
    case_type: Optional[str] = Query(None),
    court_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    advocate_id: Optional[int] = Query(None),
    client_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    query = db.query(LegalCase).filter(LegalCase.tenant_id == tenant_id).outerjoin(Client)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                LegalCase.case_number.ilike(term),
                LegalCase.court_name.ilike(term),
                LegalCase.case_type.ilike(term),
                LegalCase.opponent_name.ilike(term),
                LegalCase.case_title.ilike(term),
                Client.full_name.ilike(term),
                Client.phone.ilike(term),
            )
        )
    if case_type:
        query = query.filter(LegalCase.case_type == case_type)
    if court_name:
        query = query.filter(LegalCase.court_name.ilike(f"%{court_name}%"))
    if status:
        query = query.filter(LegalCase.status == status)
    if advocate_id:
        query = query.filter(
            or_(LegalCase.advocate_id == advocate_id, LegalCase.assistant_id == advocate_id)
        )
    if client_id:
        query = query.filter(LegalCase.client_id == client_id)

    cases = query.order_by(LegalCase.id.desc()).all()
    return [serialize_case(c, include_details=False) for c in cases]


@router.get("/{case_id}")
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    c = (
        db.query(LegalCase)
        .filter(LegalCase.id == case_id, LegalCase.tenant_id == tenant_id)
        .first()
    )
    if not c:
        raise HTTPException(status_code=404, detail="मुद्दाको विवरण भेटिएन (Case not found)")
    return serialize_case(c, include_details=True)


@router.post("")
def create_case(
    payload: LegalCaseCreate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    existing = (
        db.query(LegalCase)
        .filter(
            LegalCase.tenant_id == tenant_id,
            LegalCase.case_number == payload.case_number.strip(),
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="यो मुद्दा नम्बर पहिले नै दर्ता भइसकेको छ")

    client = (
        db.query(Client)
        .filter(Client.id == payload.client_id, Client.tenant_id == tenant_id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="चयन गरिएको क्लाइन्ट भेटिएन")

    reg_ad = payload.registration_date_ad or bs_to_ad(payload.registration_date_bs)
    next_ad = payload.next_hearing_date_ad or bs_to_ad(payload.next_hearing_date_bs)
    case_title = payload.case_title or f"{client.full_name} विरुद्ध {payload.opponent_name.strip()}"

    init_paid = max(0.0, payload.initial_paid_amount or 0.0)
    deal_amt = max(0.0, payload.deal_amount or 0.0)
    due_amt = max(0.0, deal_amt - init_paid)

    new_case = LegalCase(
        tenant_id=tenant_id,
        case_number=payload.case_number.strip(),
        filing_number=payload.filing_number,
        case_title=case_title,
        court_name=payload.court_name.strip(),
        bench_section=payload.bench_section,
        case_type=payload.case_type.strip(),
        client_id=payload.client_id,
        client_party_role=payload.client_party_role,
        opponent_name=payload.opponent_name.strip(),
        opponent_address=payload.opponent_address,
        opponent_contact=payload.opponent_contact,
        opponent_counsel=payload.opponent_counsel,
        registration_date_bs=payload.registration_date_bs.strip(),
        registration_date_ad=reg_ad,
        status=payload.status,
        deal_amount=deal_amt,
        paid_amount=init_paid,
        due_amount=due_amt,
        advocate_id=payload.advocate_id,
        assistant_id=payload.assistant_id,
        waris_name=payload.waris_name,
        next_hearing_date_bs=payload.next_hearing_date_bs,
        next_hearing_date_ad=next_ad,
        summary=payload.summary,
    )
    db.add(new_case)
    db.flush()

    if init_paid > 0:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        prefix = (tenant.receipt_prefix if tenant and tenant.receipt_prefix else "RCP").strip()
        receipt_no = (
            payload.initial_receipt_number.strip()
            if payload.initial_receipt_number
            else f"{prefix}-{new_case.id:03d}-{int(datetime.utcnow().timestamp()) % 10000:04d}"
        )
        payment = PaymentRecord(
            tenant_id=tenant_id,
            case_id=new_case.id,
            client_id=client.id,
            amount=init_paid,
            payment_date_bs=payload.registration_date_bs.strip(),
            payment_date_ad=reg_ad,
            payment_method=payload.initial_payment_method or "नगद (Cash)",
            receipt_number=receipt_no,
            purpose="पेश्की / वकालत शुल्क (Advance Fee)",
            received_by_id=current_user.id,
            remarks="मुद्दा दर्ता गर्दा प्राप्त पेश्की रकम",
        )
        db.add(payment)

    db.commit()
    db.refresh(new_case)
    return serialize_case(new_case, include_details=True)


@router.put("/{case_id}")
def update_case(
    case_id: int,
    payload: LegalCaseUpdate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    c = (
        db.query(LegalCase)
        .filter(LegalCase.id == case_id, LegalCase.tenant_id == tenant_id)
        .first()
    )
    if not c:
        raise HTTPException(status_code=404, detail="मुद्दाको विवरण भेटिएन")

    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(c, k, v)

    if "registration_date_bs" in update_data and not update_data.get("registration_date_ad"):
        c.registration_date_ad = bs_to_ad(c.registration_date_bs)
    if "next_hearing_date_bs" in update_data and not update_data.get("next_hearing_date_ad"):
        c.next_hearing_date_ad = bs_to_ad(c.next_hearing_date_bs)

    recalculate_case_financials(c, db)
    db.commit()
    db.refresh(c)
    return serialize_case(c, include_details=True)


@router.delete("/{case_id}")
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    c = (
        db.query(LegalCase)
        .filter(LegalCase.id == case_id, LegalCase.tenant_id == tenant_id)
        .first()
    )
    if not c:
        raise HTTPException(status_code=404, detail="मुद्दाको विवरण भेटिएन")
    db.delete(c)
    db.commit()
    return {"message": "मुद्दाको विवरण हटाइयो"}
