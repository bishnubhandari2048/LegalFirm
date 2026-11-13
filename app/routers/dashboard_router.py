from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    Client,
    LegalCase,
    Hearing,
    PaymentRecord,
    CaseDocument,
    StaffMember,
    CorporateEntity,
    ComplianceActivity,
    SystemModuleConfig,
    Tenant,
)
from app.auth import get_current_user, get_current_tenant_id
from app.bs_calendar import today_bs, ad_to_bs, bs_to_ad, format_bs_human

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard & Legal Utilities / ड्यासबोर्ड"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    current_bs = today_bs()
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    total_clients = db.query(Client).filter(Client.tenant_id == tenant_id).count()
    all_cases = db.query(LegalCase).filter(LegalCase.tenant_id == tenant_id).all()
    total_cases = len(all_cases)
    active_cases = sum(1 for c in all_cases if "फैसला" not in (c.status or "") and "मिलापत्र" not in (c.status or ""))
    decided_cases = total_cases - active_cases

    total_deal = sum(c.deal_amount or 0.0 for c in all_cases)
    total_paid = sum(c.paid_amount or 0.0 for c in all_cases)
    total_due = sum(c.due_amount or 0.0 for c in all_cases)

    total_advocates = (
        db.query(StaffMember)
        .filter(
            StaffMember.tenant_id == tenant_id,
            StaffMember.role.in_(["advocate", "admin"]),
        )
        .count()
    )
    total_staff = (
        db.query(StaffMember)
        .filter(StaffMember.tenant_id == tenant_id, StaffMember.role == "staff")
        .count()
    )
    total_docs = db.query(CaseDocument).filter(CaseDocument.tenant_id == tenant_id).count()
    original_docs_held = (
        db.query(CaseDocument)
        .filter(
            CaseDocument.tenant_id == tenant_id,
            CaseDocument.document_type.ilike("%मूल%"),
            CaseDocument.status.ilike("%सुरक्षित%"),
        )
        .count()
    )

    # Company Management (OCR + IRD Tax + Audit) KPIs scoped by tenant
    total_companies = db.query(CorporateEntity).filter(CorporateEntity.tenant_id == tenant_id).count()
    all_compliance = (
        db.query(ComplianceActivity)
        .filter(ComplianceActivity.tenant_id == tenant_id)
        .order_by(ComplianceActivity.due_date_bs.asc())
        .all()
    )
    pending_compliance = [
        a for a in all_compliance if "Completed" not in (a.status or "") and "सम्पन्न" not in (a.status or "")
    ]

    # Upcoming / Today's hearings (दैनिक तथा आगामी पेशी सूची)
    upcoming_cases = (
        db.query(LegalCase)
        .filter(
            LegalCase.tenant_id == tenant_id,
            LegalCase.next_hearing_date_bs.isnot(None),
            LegalCase.next_hearing_date_bs != "",
        )
        .order_by(LegalCase.next_hearing_date_bs.asc())
        .limit(12)
        .all()
    )
    cause_list = [
        {
            "case_id": c.id,
            "case_number": c.case_number,
            "court_name": c.court_name,
            "bench_section": c.bench_section or "",
            "case_type": c.case_type,
            "client_name": c.client.full_name if c.client else "",
            "client_phone": c.client.phone if c.client else "",
            "opponent_name": c.opponent_name,
            "advocate_name": c.advocate.full_name if c.advocate else "तोकिएको छैन",
            "assistant_name": c.assistant.full_name if c.assistant else "",
            "next_hearing_date_bs": c.next_hearing_date_bs,
            "next_hearing_date_bs_human": format_bs_human(c.next_hearing_date_bs),
            "status": c.status,
            "is_today": c.next_hearing_date_bs == current_bs,
        }
        for c in upcoming_cases
    ]

    # Case distribution by type
    type_counts: dict[str, int] = {}
    court_counts: dict[str, int] = {}
    for c in all_cases:
        type_counts[c.case_type] = type_counts.get(c.case_type, 0) + 1
        court_counts[c.court_name] = court_counts.get(c.court_name, 0) + 1

    # Recent hearings
    recent_hearings = (
        db.query(Hearing)
        .filter(Hearing.tenant_id == tenant_id)
        .order_by(Hearing.hearing_date_bs.desc(), Hearing.id.desc())
        .limit(6)
        .all()
    )

    # Active Module Subscriptions for this Tenant
    modules = db.query(SystemModuleConfig).filter(SystemModuleConfig.tenant_id == tenant_id).all()
    module_flags = {m.module_key: m.is_enabled for m in modules}

    return {
        "tenant_id": tenant_id,
        "tenant_name_en": tenant.firm_name_en if tenant else "",
        "tenant_name_np": tenant.firm_name_np if tenant else "",
        "today_bs": current_bs,
        "today_bs_human": format_bs_human(current_bs),
        "today_ad": date.today().isoformat(),
        "module_flags": module_flags,
        "counts": {
            "total_clients": total_clients,
            "total_cases": total_cases,
            "active_cases": active_cases,
            "decided_cases": decided_cases,
            "total_advocates": total_advocates,
            "total_staff": total_staff,
            "total_documents": total_docs,
            "original_docs_held": original_docs_held,
            "total_companies": total_companies,
            "pending_compliance_count": len(pending_compliance),
        },
        "financials": {
            "total_deal_amount": round(total_deal, 2),
            "total_paid_amount": round(total_paid, 2),
            "total_due_amount": round(total_due, 2),
            "collection_rate": round((total_paid / total_deal * 100), 1) if total_deal > 0 else 0.0,
        },
        "cause_list": cause_list,
        "upcoming_compliance": [
            {
                "id": a.id,
                "company_id": a.company_id,
                "company_name_en": a.company.company_name_en if a.company else "",
                "company_name_np": a.company.company_name_np if a.company else "",
                "category": a.category,
                "activity_type": a.activity_type,
                "fiscal_year": a.fiscal_year,
                "due_date_bs": a.due_date_bs,
                "status": a.status,
                "priority": a.priority,
            }
            for a in pending_compliance[:8]
        ],
        "case_type_distribution": type_counts,
        "court_distribution": court_counts,
        "recent_hearings": [
            {
                "id": h.id,
                "case_id": h.case_id,
                "case_number": h.legal_case.case_number if h.legal_case else "",
                "court_name": h.legal_case.court_name if h.legal_case else "",
                "hearing_date_bs": h.hearing_date_bs,
                "hearing_status": h.hearing_status,
                "next_hearing_date_bs": h.next_hearing_date_bs or "",
                "outcome": h.outcome or "",
            }
            for h in recent_hearings
        ],
    }


@router.get("/conflict-check")
def conflict_of_interest_check(
    q: str = Query(..., min_length=1, description="Name, citizenship or phone to check across clients & opponents"),
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    term = f"%{q.strip()}%"
    matched_clients = (
        db.query(Client)
        .filter(
            Client.tenant_id == tenant_id,
            or_(
                Client.full_name.ilike(term),
                Client.citizenship_no.ilike(term),
                Client.phone.ilike(term),
            ),
        )
        .all()
    )
    matched_cases = (
        db.query(LegalCase)
        .filter(
            LegalCase.tenant_id == tenant_id,
            or_(
                LegalCase.opponent_name.ilike(term),
                LegalCase.opponent_contact.ilike(term),
                LegalCase.case_number.ilike(term),
                LegalCase.case_title.ilike(term),
            ),
        )
        .all()
    )

    return {
        "query": q,
        "tenant_id": tenant_id,
        "has_conflict": len(matched_cases) > 0 or len(matched_clients) > 0,
        "matched_as_client": [
            {
                "id": cl.id,
                "full_name": cl.full_name,
                "phone": cl.phone,
                "citizenship_no": cl.citizenship_no,
                "address": cl.address,
                "cases_count": len([c for c in (cl.cases or []) if c.tenant_id == tenant_id]),
            }
            for cl in matched_clients
        ],
        "matched_in_cases_or_opponent": [
            {
                "case_id": c.id,
                "case_number": c.case_number,
                "court_name": c.court_name,
                "case_type": c.case_type,
                "client_name": c.client.full_name if c.client else "",
                "opponent_name": c.opponent_name,
                "status": c.status,
            }
            for c in matched_cases
        ],
    }


@router.get("/date-convert")
def convert_date(
    bs: Optional[str] = Query(None, description="BS date YYYY-MM-DD"),
    ad: Optional[str] = Query(None, description="AD date YYYY-MM-DD"),
):
    if bs:
        converted_ad = bs_to_ad(bs)
        return {
            "bs": bs,
            "bs_human": format_bs_human(bs),
            "ad": converted_ad.isoformat() if converted_ad else "",
        }
    if ad:
        converted_bs = ad_to_bs(ad)
        return {
            "ad": ad,
            "bs": converted_bs,
            "bs_human": format_bs_human(converted_bs),
        }
    cur_bs = today_bs()
    return {
        "ad": date.today().isoformat(),
        "bs": cur_bs,
        "bs_human": format_bs_human(cur_bs),
    }
