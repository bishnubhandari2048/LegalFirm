from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CorporateEntity, ComplianceActivity, StaffMember
from app.schemas import (
    CorporateEntityCreate,
    CorporateEntityUpdate,
    ComplianceActivityCreate,
    ComplianceActivityUpdate,
)
from app.auth import get_current_user
from app.bs_calendar import bs_to_ad, format_bs_human, today_bs

router = APIRouter(
    prefix="/api/company",
    tags=["Company Management (OCR, IRD Tax & Audit) / कम्पनी, कर तथा लेखापरीक्षण"],
)


def serialize_activity(a: ComplianceActivity) -> dict:
    comp = a.company
    return {
        "id": a.id,
        "company_id": a.company_id,
        "company_name_en": comp.company_name_en if comp else "",
        "company_name_np": comp.company_name_np or (comp.company_name_en if comp else ""),
        "ocr_registration_no": comp.ocr_registration_no if comp else "",
        "pan_vat_no": comp.pan_vat_no if comp else "",
        "ird_office": comp.ird_office if comp else "",
        "category": a.category,  # OCR | IRD_TAX | AUDIT
        "activity_type": a.activity_type,
        "fiscal_year": a.fiscal_year,
        "period_label": a.period_label or "",
        "due_date_bs": a.due_date_bs,
        "due_date_bs_human": format_bs_human(a.due_date_bs),
        "due_date_ad": a.due_date_ad.isoformat() if a.due_date_ad else "",
        "completed_date_bs": a.completed_date_bs or "",
        "next_reminder_date_bs": a.next_reminder_date_bs or a.due_date_bs,
        "status": a.status,
        "priority": a.priority,
        "reference_or_certificate_no": a.reference_or_certificate_no or "",
        "auditor_or_officer_name": a.auditor_or_officer_name or "",
        "udin_number": a.udin_number or "",
        "gov_fee_or_penalty": round(a.gov_fee_or_penalty or 0.0, 2),
        "professional_fee": round(a.professional_fee or 0.0, 2),
        "assigned_to_id": a.assigned_to_id,
        "assigned_to_name": a.assigned_to.full_name if a.assigned_to else "",
        "remarks": a.remarks or "",
    }


def serialize_company(c: CorporateEntity, include_activities: bool = False) -> dict:
    acts = c.activities or []
    pending_ocr = sum(1 for a in acts if a.category == "OCR" and "Completed" not in a.status and "सम्पन्न" not in a.status)
    pending_ird = sum(1 for a in acts if a.category == "IRD_TAX" and "Completed" not in a.status and "सम्पन्न" not in a.status)
    pending_audit = sum(1 for a in acts if a.category == "AUDIT" and "Completed" not in a.status and "सम्पन्न" not in a.status)

    next_due = ""
    next_task_title = ""
    for a in acts:
        if "Completed" not in a.status and "सम्पन्न" not in a.status:
            if not next_due or a.due_date_bs < next_due:
                next_due = a.due_date_bs
                next_task_title = a.activity_type

    data = {
        "id": c.id,
        "company_name_en": c.company_name_en,
        "company_name_np": c.company_name_np or c.company_name_en,
        "company_type": c.company_type,
        "ocr_registration_no": c.ocr_registration_no,
        "registration_date_bs": c.registration_date_bs,
        "registration_date_bs_human": format_bs_human(c.registration_date_bs),
        "camis_username": c.camis_username or "",
        "pan_vat_no": c.pan_vat_no,
        "tax_registration_type": c.tax_registration_type,
        "ird_office": c.ird_office,
        "tax_clearance_upto_fy": c.tax_clearance_upto_fy or "",
        "authorized_capital": round(c.authorized_capital or 0.0, 2),
        "issued_capital": round(c.issued_capital or 0.0, 2),
        "paidup_capital": round(c.paidup_capital or 0.0, 2),
        "shareholders_count": c.shareholders_count or 1,
        "directors_summary": c.directors_summary or "",
        "registered_address": c.registered_address,
        "contact_person": c.contact_person,
        "contact_phone": c.contact_phone,
        "contact_email": c.contact_email or "",
        "current_auditor_name": c.current_auditor_name or "",
        "auditor_ican_no": c.auditor_ican_no or "",
        "last_agm_date_bs": c.last_agm_date_bs or "",
        "last_ocr_filed_fy": c.last_ocr_filed_fy or "",
        "annual_retainer_fee": round(c.annual_retainer_fee or 0.0, 2),
        "paid_retainer_amount": round(c.paid_retainer_amount or 0.0, 2),
        "due_retainer_amount": round(c.due_retainer_amount or 0.0, 2),
        "client_id": c.client_id,
        "assigned_officer_id": c.assigned_officer_id,
        "assigned_officer_name": c.assigned_officer.full_name if c.assigned_officer else "",
        "status": c.status,
        "notes": c.notes or "",
        "pending_ocr_count": pending_ocr,
        "pending_ird_count": pending_ird,
        "pending_audit_count": pending_audit,
        "total_activities_count": len(acts),
        "next_due_date_bs": next_due,
        "next_task_title": next_task_title,
    }
    if include_activities:
        data["activities"] = [serialize_activity(a) for a in acts]
    return data


def generate_standard_periodic_activities(
    company: CorporateEntity,
    fiscal_year: str,
    officer_id: Optional[int],
    db: Session,
):
    """Auto-generate Nepal Statutory OCR, IRD Tax & Audit periodic checklist for a company."""
    fy_prefix = fiscal_year.split("/")[0] if "/" in fiscal_year else "2083"
    standard_items = [
        # 1. OCR Activities
        ComplianceActivity(
            company_id=company.id,
            category="OCR",
            activity_type="Section 78 Annual Return & AGM Minutes Filing (दफा ७८ वार्षिक विवरण तथा साधारण सभा)",
            fiscal_year=fiscal_year,
            period_label="Poush End Deadline (पुस मसान्त)",
            due_date_bs=f"{fy_prefix}-09-29",
            due_date_ad=bs_to_ad(f"{fy_prefix}-09-29"),
            next_reminder_date_bs=f"{fy_prefix}-09-15",
            status="Pending (बाँकी)",
            priority="Critical",
            assigned_to_id=officer_id,
            remarks="कम्पनी ऐन, २०६३ दफा ७८ बमोजिम पुस मसान्तभित्र लेखापरीक्षण प्रतिवेदन र साधारण सभा निर्णय पेश गर्नुपर्ने (अन्यथा जरिवाना लाग्ने)।",
        ),
        ComplianceActivity(
            company_id=company.id,
            category="OCR",
            activity_type="Section 51 Shareholding & Capital Lagat Report (दफा ५१ शेयर लगत विवरण)",
            fiscal_year=fiscal_year,
            period_label="Annual Share Lagat",
            due_date_bs=f"{fy_prefix}-09-29",
            due_date_ad=bs_to_ad(f"{fy_prefix}-09-29"),
            next_reminder_date_bs=f"{fy_prefix}-09-10",
            status="Pending (बाँकी)",
            priority="High",
            assigned_to_id=officer_id,
            remarks="शेयरधनी दर्ता किताब र शेयर लगत अद्यावधिक विवरण।",
        ),
        # 2. IRD Tax Activities
        ComplianceActivity(
            company_id=company.id,
            category="IRD_TAX",
            activity_type="Monthly VAT & e-TDS Return Filing (मासिक मु.अ.कर तथा ई-टीडीएस विवरण)",
            fiscal_year=fiscal_year,
            period_label="25th of Month (महिनाको २५ गतेभित्र)",
            due_date_bs=f"{fy_prefix}-08-25",
            due_date_ad=bs_to_ad(f"{fy_prefix}-08-25"),
            next_reminder_date_bs=f"{fy_prefix}-08-20",
            status="Pending (बाँकी)",
            priority="Critical",
            assigned_to_id=officer_id,
            remarks="आन्तरिक राजस्व विभाग (IRD Portal) मा खरिद-बिक्री खाता रुजु गरी भ्याट र अग्रिम कर कट्टी (e-TDS) दाखिला।",
        ),
        ComplianceActivity(
            company_id=company.id,
            category="IRD_TAX",
            activity_type="Estimated Income Tax Return & 1st Installment 40% (अनुमानित आयकर विवरण र प्रथम किस्ता ४०%)",
            fiscal_year=fiscal_year,
            period_label="Poush End (पुस मसान्त)",
            due_date_bs=f"{fy_prefix}-09-29",
            due_date_ad=bs_to_ad(f"{fy_prefix}-09-29"),
            next_reminder_date_bs=f"{fy_prefix}-09-20",
            status="Pending (बाँकी)",
            priority="High",
            assigned_to_id=officer_id,
            remarks="आयकर ऐन, २०५८ बमोजिम पुस मसान्तभित्र अनुमानित करको ४०% प्रथम किस्ता दाखिला।",
        ),
        ComplianceActivity(
            company_id=company.id,
            category="IRD_TAX",
            activity_type="Annual Income Tax Return D-03 & Tax Clearance Certificate (आयकर विवरण D-03 र कर चुक्ता प्रमाणपत्र)",
            fiscal_year=fiscal_year,
            period_label="Ashwin / Poush Extended",
            due_date_bs=f"{fy_prefix}-09-25",
            due_date_ad=bs_to_ad(f"{fy_prefix}-09-25"),
            next_reminder_date_bs=f"{fy_prefix}-09-10",
            status="In Progress (प्रक्रियामा)",
            priority="Critical",
            assigned_to_id=officer_id,
            remarks="लेखापरीक्षण प्रतिवेदन संलग्न गरी D-03 पेश गर्ने र कर चुक्ता प्रमाणपत्र (Tax Clearance) लिने।",
        ),
        # 3. Statutory Audit & AGM Activities
        ComplianceActivity(
            company_id=company.id,
            category="AUDIT",
            activity_type="Statutory Audit Report & UDIN Verification (वैधानिक लेखापरीक्षण र UDIN प्रमाणीकरण)",
            fiscal_year=fiscal_year,
            period_label=f"FY {fiscal_year} Audit",
            due_date_bs=f"{fy_prefix}-08-30",
            due_date_ad=bs_to_ad(f"{fy_prefix}-08-30"),
            next_reminder_date_bs=f"{fy_prefix}-08-15",
            status="In Progress (प्रक्रियामा)",
            priority="High",
            auditor_or_officer_name=company.current_auditor_name,
            assigned_to_id=officer_id,
            remarks="ICAN दर्ता लेखापरीक्षकबाट वित्तीय विवरण (Balance Sheet, P&L, Cashflow) लेखापरीक्षण र UDIN जारी।",
        ),
    ]
    db.add_all(standard_items)


@router.get("/summary")
def get_company_module_summary(
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    cur_bs = today_bs()
    companies = db.query(CorporateEntity).order_by(CorporateEntity.id.desc()).all()
    activities = db.query(ComplianceActivity).order_by(ComplianceActivity.due_date_bs.asc()).all()

    ocr_pending = [a for a in activities if a.category == "OCR" and "Completed" not in a.status and "सम्पन्न" not in a.status]
    ird_pending = [a for a in activities if a.category == "IRD_TAX" and "Completed" not in a.status and "सम्पन्न" not in a.status]
    audit_pending = [a for a in activities if a.category == "AUDIT" and "Completed" not in a.status and "सम्पन्न" not in a.status]
    completed_all = [a for a in activities if "Completed" in a.status or "सम्पन्न" in a.status]

    total_retainer = sum(c.annual_retainer_fee or 0.0 for c in companies)
    total_paid = sum(c.paid_retainer_amount or 0.0 for c in companies)
    total_due = sum(c.due_retainer_amount or 0.0 for c in companies)

    # Upcoming / Due Reminders
    upcoming_reminders = [
        serialize_activity(a)
        for a in activities
        if "Completed" not in a.status and "सम्पन्न" not in a.status
    ][:12]

    return {
        "today_bs": cur_bs,
        "counts": {
            "total_companies": len(companies),
            "ocr_pending": len(ocr_pending),
            "ird_tax_pending": len(ird_pending),
            "audit_pending": len(audit_pending),
            "completed_activities": len(completed_all),
        },
        "financials": {
            "total_retainer_fee": round(total_retainer, 2),
            "total_paid_retainer": round(total_paid, 2),
            "total_due_retainer": round(total_due, 2),
        },
        "upcoming_reminders": upcoming_reminders,
    }


@router.get("/entities")
def list_companies(
    search: Optional[str] = Query(None),
    company_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    query = db.query(CorporateEntity)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                CorporateEntity.company_name_en.ilike(term),
                CorporateEntity.company_name_np.ilike(term),
                CorporateEntity.ocr_registration_no.ilike(term),
                CorporateEntity.pan_vat_no.ilike(term),
                CorporateEntity.contact_person.ilike(term),
                CorporateEntity.ird_office.ilike(term),
            )
        )
    if company_type:
        query = query.filter(CorporateEntity.company_type == company_type)

    items = query.order_by(CorporateEntity.id.desc()).all()
    return [serialize_company(c, include_activities=False) for c in items]


@router.get("/entities/{company_id}")
def get_company_detail(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    comp = db.query(CorporateEntity).filter(CorporateEntity.id == company_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="कम्पनीको विवरण भेटिएन (Company not found)")
    return serialize_company(comp, include_activities=True)


@router.post("/entities")
def create_company(
    payload: CorporateEntityCreate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    existing = (
        db.query(CorporateEntity)
        .filter(CorporateEntity.ocr_registration_no == payload.ocr_registration_no.strip())
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="यो कम्पनी दर्ता नं. (OCR No.) पहिले नै दर्ता छ")

    retainer = max(0.0, payload.annual_retainer_fee or 0.0)
    paid = max(0.0, payload.paid_retainer_amount or 0.0)
    due = max(0.0, retainer - paid)

    comp = CorporateEntity(
        company_name_en=payload.company_name_en.strip(),
        company_name_np=payload.company_name_np.strip() if payload.company_name_np else payload.company_name_en.strip(),
        company_type=payload.company_type,
        ocr_registration_no=payload.ocr_registration_no.strip(),
        registration_date_bs=payload.registration_date_bs.strip(),
        registration_date_ad=bs_to_ad(payload.registration_date_bs),
        camis_username=payload.camis_username,
        pan_vat_no=payload.pan_vat_no.strip(),
        tax_registration_type=payload.tax_registration_type,
        ird_office=payload.ird_office,
        tax_clearance_upto_fy=payload.tax_clearance_upto_fy,
        authorized_capital=payload.authorized_capital,
        issued_capital=payload.issued_capital,
        paidup_capital=payload.paidup_capital,
        shareholders_count=payload.shareholders_count,
        directors_summary=payload.directors_summary,
        registered_address=payload.registered_address,
        contact_person=payload.contact_person,
        contact_phone=payload.contact_phone,
        contact_email=payload.contact_email,
        current_auditor_name=payload.current_auditor_name,
        auditor_ican_no=payload.auditor_ican_no,
        last_agm_date_bs=payload.last_agm_date_bs,
        last_ocr_filed_fy=payload.last_ocr_filed_fy,
        annual_retainer_fee=retainer,
        paid_retainer_amount=paid,
        due_retainer_amount=due,
        client_id=payload.client_id,
        assigned_officer_id=payload.assigned_officer_id or current_user.id,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(comp)
    db.flush()

    if payload.auto_generate_periodic_tasks:
        generate_standard_periodic_activities(
            comp, "2083/84", comp.assigned_officer_id, db
        )

    db.commit()
    db.refresh(comp)
    return serialize_company(comp, include_activities=True)


@router.put("/entities/{company_id}")
def update_company(
    company_id: int,
    payload: CorporateEntityUpdate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    comp = db.query(CorporateEntity).filter(CorporateEntity.id == company_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="कम्पनी भेटिएन")

    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(comp, k, v)

    comp.due_retainer_amount = max(0.0, (comp.annual_retainer_fee or 0.0) - (comp.paid_retainer_amount or 0.0))
    db.commit()
    db.refresh(comp)
    return serialize_company(comp, include_activities=True)


@router.delete("/entities/{company_id}")
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    comp = db.query(CorporateEntity).filter(CorporateEntity.id == company_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="कम्पनी भेटिएन")
    db.delete(comp)
    db.commit()
    return {"message": "कम्पनीको विवरण हटाइयो"}


@router.get("/activities")
def list_compliance_activities(
    company_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None, description="OCR | IRD_TAX | AUDIT"),
    status: Optional[str] = Query(None),
    fiscal_year: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    query = db.query(ComplianceActivity).join(CorporateEntity)
    if company_id:
        query = query.filter(ComplianceActivity.company_id == company_id)
    if category:
        query = query.filter(ComplianceActivity.category == category)
    if status:
        query = query.filter(ComplianceActivity.status == status)
    if fiscal_year:
        query = query.filter(ComplianceActivity.fiscal_year == fiscal_year)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                ComplianceActivity.activity_type.ilike(term),
                CorporateEntity.company_name_en.ilike(term),
                CorporateEntity.company_name_np.ilike(term),
                CorporateEntity.pan_vat_no.ilike(term),
                ComplianceActivity.reference_or_certificate_no.ilike(term),
                ComplianceActivity.udin_number.ilike(term),
            )
        )

    items = query.order_by(ComplianceActivity.due_date_bs.asc(), ComplianceActivity.id.desc()).all()
    return [serialize_activity(a) for a in items]


@router.post("/activities")
def create_compliance_activity(
    payload: ComplianceActivityCreate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    comp = db.query(CorporateEntity).filter(CorporateEntity.id == payload.company_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="कम्पनी भेटिएन")

    act = ComplianceActivity(
        company_id=comp.id,
        category=payload.category,
        activity_type=payload.activity_type.strip(),
        fiscal_year=payload.fiscal_year,
        period_label=payload.period_label,
        due_date_bs=payload.due_date_bs.strip(),
        due_date_ad=bs_to_ad(payload.due_date_bs),
        completed_date_bs=payload.completed_date_bs,
        next_reminder_date_bs=payload.next_reminder_date_bs or payload.due_date_bs.strip(),
        status=payload.status,
        priority=payload.priority,
        reference_or_certificate_no=payload.reference_or_certificate_no,
        auditor_or_officer_name=payload.auditor_or_officer_name,
        udin_number=payload.udin_number,
        gov_fee_or_penalty=payload.gov_fee_or_penalty,
        professional_fee=payload.professional_fee,
        assigned_to_id=payload.assigned_to_id or current_user.id,
        remarks=payload.remarks,
    )
    db.add(act)

    # If a Tax Clearance activity is marked Completed, update the parent company's tax_clearance_upto_fy
    if "Tax Clearance" in act.activity_type and ("Completed" in act.status or "सम्पन्न" in act.status):
        comp.tax_clearance_upto_fy = act.fiscal_year

    db.commit()
    db.refresh(act)
    return serialize_activity(act)


@router.put("/activities/{activity_id}")
def update_compliance_activity(
    activity_id: int,
    payload: ComplianceActivityUpdate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    act = db.query(ComplianceActivity).filter(ComplianceActivity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="कार्य विवरण भेटिएन")

    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(act, k, v)

    if act.due_date_bs:
        act.due_date_ad = bs_to_ad(act.due_date_bs)

    if act.company and "Tax Clearance" in (act.activity_type or "") and ("Completed" in (act.status or "") or "सम्पन्न" in (act.status or "")):
        act.company.tax_clearance_upto_fy = act.fiscal_year

    db.commit()
    db.refresh(act)
    return serialize_activity(act)


@router.delete("/activities/{activity_id}")
def delete_compliance_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
):
    act = db.query(ComplianceActivity).filter(ComplianceActivity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="कार्य विवरण भेटिएन")
    db.delete(act)
    db.commit()
    return {"message": "कार्य विवरण हटाइयो"}
