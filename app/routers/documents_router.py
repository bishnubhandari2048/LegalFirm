import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import CaseDocument, LegalCase, Client, StaffMember
from app.schemas import CaseDocumentCreate, CaseDocumentUpdate
from app.auth import get_current_user, get_current_tenant_id
from app.bs_calendar import bs_to_ad, format_bs_human

router = APIRouter(prefix="/api/documents", tags=["Documents / कागजात सम्बन्धी विवरण"])


def serialize_document(d: CaseDocument) -> dict:
    c = d.legal_case
    cl = d.client or (c.client if c else None)
    return {
        "id": d.id,
        "tenant_id": d.tenant_id,
        "case_id": d.case_id,
        "case_number": c.case_number if c else "",
        "court_name": c.court_name if c else "",
        "case_type": c.case_type if c else "",
        "client_id": d.client_id or (c.client_id if c else None),
        "client_name": cl.full_name if cl else "",
        "document_name": d.document_name,
        "document_type": d.document_type,
        "status": d.status,
        "received_date_bs": d.received_date_bs,
        "received_date_bs_human": format_bs_human(d.received_date_bs),
        "received_date_ad": d.received_date_ad.isoformat() if d.received_date_ad else "",
        "returned_date_bs": d.returned_date_bs or "",
        "returned_date_bs_human": format_bs_human(d.returned_date_bs) if d.returned_date_bs else "-",
        "returned_date_ad": d.returned_date_ad.isoformat() if d.returned_date_ad else "",
        "handover_person": d.handover_person or "",
        "file_path": d.file_path or "",
        "file_name": d.file_name or "",
        "remarks": d.remarks or "",
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


@router.get("")
def list_documents(
    case_id: Optional[int] = Query(None),
    client_id: Optional[int] = Query(None),
    document_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    query = (
        db.query(CaseDocument)
        .filter(CaseDocument.tenant_id == tenant_id)
        .join(LegalCase)
    )
    if case_id:
        query = query.filter(CaseDocument.case_id == case_id)
    if client_id:
        query = query.filter(
            (CaseDocument.client_id == client_id) | (LegalCase.client_id == client_id)
        )
    if document_type:
        query = query.filter(CaseDocument.document_type == document_type)
    if status:
        query = query.filter(CaseDocument.status == status)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            (CaseDocument.document_name.ilike(term))
            | (LegalCase.case_number.ilike(term))
            | (CaseDocument.handover_person.ilike(term))
            | (CaseDocument.remarks.ilike(term))
        )

    docs = query.order_by(CaseDocument.id.desc()).all()
    return [serialize_document(d) for d in docs]


@router.post("")
def create_document(
    payload: CaseDocumentCreate,
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

    rec_ad = payload.received_date_ad or bs_to_ad(payload.received_date_bs)
    ret_ad = payload.returned_date_ad or bs_to_ad(payload.returned_date_bs)

    doc = CaseDocument(
        tenant_id=tenant_id,
        case_id=legal_case.id,
        client_id=payload.client_id or legal_case.client_id,
        document_name=payload.document_name.strip(),
        document_type=payload.document_type,
        status=payload.status,
        received_date_bs=payload.received_date_bs.strip(),
        received_date_ad=rec_ad,
        returned_date_bs=payload.returned_date_bs.strip() if payload.returned_date_bs else None,
        returned_date_ad=ret_ad,
        handover_person=payload.handover_person,
        remarks=payload.remarks,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return serialize_document(doc)


@router.post("/upload")
async def create_document_with_file(
    case_id: int = Form(...),
    document_name: str = Form(...),
    document_type: str = Form("प्रतिलिपि (Copy)"),
    status: str = Form("कार्यालयमा सुरक्षित (In Office)"),
    received_date_bs: str = Form(...),
    returned_date_bs: Optional[str] = Form(None),
    handover_person: Optional[str] = Form(None),
    remarks: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
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
        raise HTTPException(status_code=404, detail="सम्बन्धित मुद्दा भेटिएन")

    saved_url = None
    orig_filename = None
    if file and file.filename:
        orig_filename = file.filename
        ext = os.path.splitext(file.filename)[1] or ".bin"
        unique_name = f"t{tenant_id}_doc_{case_id}_{uuid.uuid4().hex[:8]}{ext}"
        dest = settings.UPLOAD_DIR / unique_name
        content = await file.read()
        with open(dest, "wb") as f:
            f.write(content)
        saved_url = f"/static/uploads/{unique_name}"

    doc = CaseDocument(
        tenant_id=tenant_id,
        case_id=legal_case.id,
        client_id=legal_case.client_id,
        document_name=document_name.strip(),
        document_type=document_type,
        status=status,
        received_date_bs=received_date_bs.strip(),
        received_date_ad=bs_to_ad(received_date_bs),
        returned_date_bs=returned_date_bs.strip() if returned_date_bs else None,
        returned_date_ad=bs_to_ad(returned_date_bs) if returned_date_bs else None,
        handover_person=handover_person,
        file_path=saved_url,
        file_name=orig_filename,
        remarks=remarks,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return serialize_document(doc)


@router.put("/{doc_id}")
def update_document(
    doc_id: int,
    payload: CaseDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    doc = (
        db.query(CaseDocument)
        .filter(CaseDocument.id == doc_id, CaseDocument.tenant_id == tenant_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="कागजातको विवरण भेटिएन")

    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(doc, k, v)

    if doc.received_date_bs:
        doc.received_date_ad = bs_to_ad(doc.received_date_bs)
    if doc.returned_date_bs:
        doc.returned_date_ad = bs_to_ad(doc.returned_date_bs)
        if "क्लाइन्टलाई फिर्ता" not in (doc.status or ""):
            doc.status = "क्लाइन्टलाई फिर्ता (Returned to Client)"

    db.commit()
    db.refresh(doc)
    return serialize_document(doc)


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    doc = (
        db.query(CaseDocument)
        .filter(CaseDocument.id == doc_id, CaseDocument.tenant_id == tenant_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="कागजातको विवरण भेटिएन")
    db.delete(doc)
    db.commit()
    return {"message": "कागजात विवरण हटाइयो"}
