from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Hearing, LegalCase, StaffMember
from app.schemas import HearingCreate, HearingUpdate
from app.auth import get_current_user
from app.bs_calendar import bs_to_ad, format_bs_human

router = APIRouter(prefix="/api/hearings", tags=["Hearings (Peshi) / पेशी विवरण"])


def serialize_hearing(h: Hearing) -> dict:
    c = h.legal_case
    return {
        "id": h.id,
        "case_id": h.case_id,
        "case_number": c.case_number if c else "",
        "case_title": c.case_title if c else "",
        "court_name": c.court_name if c else "",
        "case_type": c.case_type if c else "",
        "client_name": c.client.full_name if (c and c.client) else "",
        "client_phone": c.client.phone if (c and c.client) else "",
        "opponent_name": c.opponent_name if c else "",
        "advocate_name": c.advocate.full_name if (c and c.advocate) else "",
        "hearing_date_bs": h.hearing_date_bs,
        "hearing_date_bs_human": format_bs_human(h.hearing_date_bs),
        "hearing_date_ad": h.hearing_date_ad.isoformat() if h.hearing_date_ad else "",
        "hearing_status": h.hearing_status,
        "bench_or_judge": h.bench_or_judge or "",
        "next_hearing_date_bs": h.next_hearing_date_bs or "",
        "next_hearing_date_bs_human": format_bs_human(h.next_hearing_date_bs) if h.next_hearing_date_bs else "-",
        "next_hearing_date_ad": h.next_hearing_date_ad.isoformat() if h.next_hearing_date_ad else "",
        "outcome": h.outcome or "",
        "attended_by_id": h.attended_by_id,
        "attended_by_name": h.attended_by.full_name if h.attended_by else "",
        "remarks": h.remarks or "",
        "created_at": h.created_at.isoformat() if h.created_at else None,
    }


@router.get("")
def list_hearings(
    case_id: Optional[int] = Query(None),
    hearing_status: Optional[str] = Query(None),
    date_bs: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    query = db.query(Hearing).join(LegalCase)
    if case_id:
        query = query.filter(Hearing.case_id == case_id)
    if hearing_status:
        query = query.filter(Hearing.hearing_status == hearing_status)
    if date_bs:
        query = query.filter(
            (Hearing.hearing_date_bs == date_bs) | (Hearing.next_hearing_date_bs == date_bs)
        )
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            (LegalCase.case_number.ilike(term))
            | (LegalCase.court_name.ilike(term))
            | (LegalCase.opponent_name.ilike(term))
            | (Hearing.outcome.ilike(term))
            | (Hearing.hearing_status.ilike(term))
        )

    items = query.order_by(Hearing.hearing_date_bs.desc(), Hearing.id.desc()).all()
    return [serialize_hearing(h) for h in items]


@router.post("")
def create_hearing(
    payload: HearingCreate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    legal_case = db.query(LegalCase).filter(LegalCase.id == payload.case_id).first()
    if not legal_case:
        raise HTTPException(status_code=404, detail="सम्बन्धित मुद्दा भेटिएन")

    h_ad = payload.hearing_date_ad or bs_to_ad(payload.hearing_date_bs)
    next_ad = payload.next_hearing_date_ad or bs_to_ad(payload.next_hearing_date_bs)

    hearing = Hearing(
        case_id=payload.case_id,
        hearing_date_bs=payload.hearing_date_bs.strip(),
        hearing_date_ad=h_ad,
        hearing_status=payload.hearing_status.strip(),
        bench_or_judge=payload.bench_or_judge,
        next_hearing_date_bs=payload.next_hearing_date_bs.strip() if payload.next_hearing_date_bs else None,
        next_hearing_date_ad=next_ad,
        outcome=payload.outcome,
        attended_by_id=payload.attended_by_id or current_user.id,
        remarks=payload.remarks,
    )
    db.add(hearing)

    # Automatically sync next hearing date and status on the parent case
    if payload.next_hearing_date_bs:
        legal_case.next_hearing_date_bs = payload.next_hearing_date_bs.strip()
        legal_case.next_hearing_date_ad = next_ad
    if payload.update_case_status:
        legal_case.status = payload.update_case_status
    elif "फैसला" in payload.hearing_status:
        legal_case.status = "फैसला भएको (Decided)"

    db.commit()
    db.refresh(hearing)
    return serialize_hearing(hearing)


@router.put("/{hearing_id}")
def update_hearing(
    hearing_id: int,
    payload: HearingUpdate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    hearing = db.query(Hearing).filter(Hearing.id == hearing_id).first()
    if not hearing:
        raise HTTPException(status_code=404, detail="पेशी विवरण भेटिएन")

    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(hearing, k, v)

    if "hearing_date_bs" in update_data and not update_data.get("hearing_date_ad"):
        hearing.hearing_date_ad = bs_to_ad(hearing.hearing_date_bs)
    if "next_hearing_date_bs" in update_data and not update_data.get("next_hearing_date_ad"):
        hearing.next_hearing_date_ad = bs_to_ad(hearing.next_hearing_date_bs)

    if hearing.next_hearing_date_bs and hearing.legal_case:
        hearing.legal_case.next_hearing_date_bs = hearing.next_hearing_date_bs
        hearing.legal_case.next_hearing_date_ad = hearing.next_hearing_date_ad

    db.commit()
    db.refresh(hearing)
    return serialize_hearing(hearing)


@router.delete("/{hearing_id}")
def delete_hearing(
    hearing_id: int,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    hearing = db.query(Hearing).filter(Hearing.id == hearing_id).first()
    if not hearing:
        raise HTTPException(status_code=404, detail="पेशी विवरण भेटिएन")
    db.delete(hearing)
    db.commit()
    return {"message": "पेशी विवरण हटाइयो"}
