from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import PaymentRecord, LegalCase, Client, StaffMember, Tenant
from app.schemas import PaymentCreate, DealAmountUpdate
from app.auth import get_current_user, get_current_tenant_id
from app.bs_calendar import bs_to_ad, format_bs_human
from app.routers.cases_router import recalculate_case_financials

router = APIRouter(prefix="/api/finance", tags=["Financials & Receipts / आर्थिक विवरण"])


def serialize_payment(p: PaymentRecord) -> dict:
    c = p.legal_case
    cl = p.client or (c.client if c else None)
    return {
        "id": p.id,
        "tenant_id": p.tenant_id,
        "case_id": p.case_id,
        "case_number": c.case_number if c else "",
        "court_name": c.court_name if c else "",
        "case_type": c.case_type if c else "",
        "deal_amount": round(c.deal_amount or 0.0, 2) if c else 0.0,
        "case_paid_amount": round(c.paid_amount or 0.0, 2) if c else 0.0,
        "case_due_amount": round(c.due_amount or 0.0, 2) if c else 0.0,
        "client_id": p.client_id,
        "client_name": cl.full_name if cl else "",
        "client_phone": cl.phone if cl else "",
        "client_address": cl.address if cl else "",
        "amount": round(p.amount, 2),
        "payment_date_bs": p.payment_date_bs,
        "payment_date_bs_human": format_bs_human(p.payment_date_bs),
        "payment_date_ad": p.payment_date_ad.isoformat() if p.payment_date_ad else "",
        "payment_method": p.payment_method,
        "receipt_number": p.receipt_number,
        "purpose": p.purpose,
        "reference_no": p.reference_no or "",
        "remarks": p.remarks or "",
        "received_by_id": p.received_by_id,
        "received_by_name": p.received_by.full_name if p.received_by else "",
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


@router.get("/summary")
def get_financial_summary(
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    cases = db.query(LegalCase).filter(LegalCase.tenant_id == tenant_id).all()
    payments = (
        db.query(PaymentRecord)
        .filter(PaymentRecord.tenant_id == tenant_id)
        .order_by(PaymentRecord.id.desc())
        .all()
    )

    total_deal = sum(c.deal_amount or 0.0 for c in cases)
    total_paid = sum(c.paid_amount or 0.0 for c in cases)
    total_due = sum(c.due_amount or 0.0 for c in cases)

    # Breakdown by payment method
    method_breakdown: dict[str, float] = {}
    for p in payments:
        method_breakdown[p.payment_method] = round(
            method_breakdown.get(p.payment_method, 0.0) + p.amount, 2
        )

    # Case-wise financial ledger
    case_ledgers = [
        {
            "case_id": c.id,
            "case_number": c.case_number,
            "case_type": c.case_type,
            "court_name": c.court_name,
            "client_id": c.client_id,
            "client_name": c.client.full_name if c.client else "",
            "client_phone": c.client.phone if c.client else "",
            "deal_amount": round(c.deal_amount or 0.0, 2),
            "paid_amount": round(c.paid_amount or 0.0, 2),
            "due_amount": round(c.due_amount or 0.0, 2),
            "payment_status": (
                "चुक्ता (Paid)"
                if (c.deal_amount or 0) > 0 and (c.due_amount or 0) <= 0
                else ("आंशिक बाँकी (Partial)" if (c.paid_amount or 0) > 0 else "बाँकी (Unpaid)")
            ),
            "payments_count": len(c.payments or []),
        }
        for c in cases
    ]

    return {
        "total_deal_amount": round(total_deal, 2),
        "total_paid_amount": round(total_paid, 2),
        "total_due_amount": round(total_due, 2),
        "total_transactions": len(payments),
        "method_breakdown": method_breakdown,
        "case_ledgers": case_ledgers,
    }


@router.get("/payments")
def list_payments(
    case_id: Optional[int] = Query(None),
    client_id: Optional[int] = Query(None),
    payment_method: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    query = (
        db.query(PaymentRecord)
        .filter(PaymentRecord.tenant_id == tenant_id)
        .join(LegalCase)
        .join(Client, PaymentRecord.client_id == Client.id)
    )
    if case_id:
        query = query.filter(PaymentRecord.case_id == case_id)
    if client_id:
        query = query.filter(PaymentRecord.client_id == client_id)
    if payment_method:
        query = query.filter(PaymentRecord.payment_method == payment_method)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            (PaymentRecord.receipt_number.ilike(term))
            | (LegalCase.case_number.ilike(term))
            | (Client.full_name.ilike(term))
            | (PaymentRecord.payment_method.ilike(term))
        )

    records = query.order_by(PaymentRecord.id.desc()).all()
    return [serialize_payment(p) for p in records]


@router.post("/payments")
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    legal_case = (
        db.query(LegalCase)
        .filter(LegalCase.id == payload.case_id, LegalCase.tenant_id == tenant_id)
        .first()
    )
    if not legal_case:
        raise HTTPException(status_code=404, detail="सम्बन्धित मुद्दा भेटिएन")

    client_id = payload.client_id or legal_case.client_id

    if payload.receipt_number and payload.receipt_number.strip():
        receipt_no = payload.receipt_number.strip()
        exists = (
            db.query(PaymentRecord)
            .filter(
                PaymentRecord.tenant_id == tenant_id,
                PaymentRecord.receipt_number == receipt_no,
            )
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail="यो रसिद नम्बर पहिले नै प्रयोग भइसकेको छ")
    else:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        prefix = (tenant.receipt_prefix if tenant and tenant.receipt_prefix else "RCP").strip()
        count = db.query(PaymentRecord).filter(PaymentRecord.tenant_id == tenant_id).count() + 1
        receipt_no = f"{prefix}-2083-{count:04d}-{int(datetime.utcnow().timestamp()) % 1000:03d}"

    pay_ad = payload.payment_date_ad or bs_to_ad(payload.payment_date_bs)

    payment = PaymentRecord(
        tenant_id=tenant_id,
        case_id=legal_case.id,
        client_id=client_id,
        amount=payload.amount,
        payment_date_bs=payload.payment_date_bs.strip(),
        payment_date_ad=pay_ad,
        payment_method=payload.payment_method,
        receipt_number=receipt_no,
        purpose=payload.purpose,
        reference_no=payload.reference_no,
        remarks=payload.remarks,
        received_by_id=payload.received_by_id or current_user.id,
    )
    db.add(payment)
    db.flush()
    db.refresh(legal_case)
    recalculate_case_financials(legal_case, db)
    db.commit()
    db.refresh(payment)
    return serialize_payment(payment)


@router.put("/cases/{case_id}/deal")
def update_case_deal_amount(
    case_id: int,
    payload: DealAmountUpdate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    legal_case = (
        db.query(LegalCase)
        .filter(LegalCase.id == case_id, LegalCase.tenant_id == tenant_id)
        .first()
    )
    if not legal_case:
        raise HTTPException(status_code=404, detail="मुद्दा भेटिएन")

    legal_case.deal_amount = payload.deal_amount
    recalculate_case_financials(legal_case, db)
    db.commit()
    db.refresh(legal_case)
    return {
        "case_id": legal_case.id,
        "case_number": legal_case.case_number,
        "deal_amount": legal_case.deal_amount,
        "paid_amount": legal_case.paid_amount,
        "due_amount": legal_case.due_amount,
    }


@router.delete("/payments/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    payment = (
        db.query(PaymentRecord)
        .filter(PaymentRecord.id == payment_id, PaymentRecord.tenant_id == tenant_id)
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="भुक्तानी विवरण भेटिएन")
    legal_case = payment.legal_case
    db.delete(payment)
    db.flush()
    if legal_case:
        db.refresh(legal_case)
        recalculate_case_financials(legal_case, db)
    db.commit()
    return {"message": "भुक्तानी रसिद विवरण हटाइयो"}
