from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Client, LegalCase, StaffMember
from app.schemas import ClientCreate, ClientUpdate
from app.auth import get_current_user

router = APIRouter(prefix="/api/clients", tags=["Clients / क्लाइन्टको विवरण"])


def serialize_client(client: Client) -> dict:
    cases = client.cases or []
    total_deal = sum(c.deal_amount or 0.0 for c in cases)
    total_paid = sum(c.paid_amount or 0.0 for c in cases)
    total_due = sum(c.due_amount or 0.0 for c in cases)
    return {
        "id": client.id,
        "first_name": client.first_name,
        "last_name": client.last_name,
        "full_name": client.full_name,
        "address": client.address,
        "district": client.district or "",
        "phone": client.phone,
        "alt_phone": client.alt_phone or "",
        "email": client.email or "",
        "citizenship_no": client.citizenship_no,
        "citizenship_district": client.citizenship_district or "",
        "citizenship_issue_date_bs": client.citizenship_issue_date_bs or "",
        "father_or_spouse_name": client.father_or_spouse_name or "",
        "occupation": client.occupation or "",
        "notes": client.notes or "",
        "case_count": len(cases),
        "total_deal": round(total_deal, 2),
        "total_paid": round(total_paid, 2),
        "total_due": round(total_due, 2),
        "cases": [
            {
                "id": c.id,
                "case_number": c.case_number,
                "court_name": c.court_name,
                "case_type": c.case_type,
                "opponent_name": c.opponent_name,
                "status": c.status,
                "next_hearing_date_bs": c.next_hearing_date_bs or "",
            }
            for c in cases
        ],
        "created_at": client.created_at.isoformat() if client.created_at else None,
    }


@router.get("")
def list_clients(
    search: Optional[str] = Query(None, description="Search by name, phone, citizenship, address"),
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    query = db.query(Client)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Client.full_name.ilike(term),
                Client.first_name.ilike(term),
                Client.last_name.ilike(term),
                Client.phone.ilike(term),
                Client.citizenship_no.ilike(term),
                Client.address.ilike(term),
                Client.email.ilike(term),
            )
        )
    clients = query.order_by(Client.id.desc()).all()
    return [serialize_client(c) for c in clients]


@router.get("/{client_id}")
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="क्लाइन्ट भेटिएन (Client not found)")
    return serialize_client(client)


@router.post("")
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    full_name = f"{payload.first_name.strip()} {payload.last_name.strip()}".strip()
    client = Client(
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        full_name=full_name,
        address=payload.address.strip(),
        district=payload.district,
        phone=payload.phone.strip(),
        alt_phone=payload.alt_phone,
        email=payload.email.strip() if payload.email else None,
        citizenship_no=payload.citizenship_no.strip(),
        citizenship_district=payload.citizenship_district,
        citizenship_issue_date_bs=payload.citizenship_issue_date_bs,
        father_or_spouse_name=payload.father_or_spouse_name,
        occupation=payload.occupation,
        notes=payload.notes,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return serialize_client(client)


@router.put("/{client_id}")
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="क्लाइन्ट भेटिएन (Client not found)")

    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(client, k, v)

    client.full_name = f"{client.first_name.strip()} {client.last_name.strip()}".strip()
    db.commit()
    db.refresh(client)
    return serialize_client(client)


@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="क्लाइन्ट भेटिएन")
    db.delete(client)
    db.commit()
    return {"message": "क्लाइन्टको विवरण हटाइयो"}
