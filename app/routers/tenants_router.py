from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    Tenant,
    TenantLOV,
    SystemModuleConfig,
    StaffMember,
    Client,
    LegalCase,
    Hearing,
    PaymentRecord,
    CaseDocument,
    CorporateEntity,
    ComplianceActivity,
)
from app.schemas import TenantCreate, TenantUpdate, TenantLOVCreate, TenantLOVUpdate
from app.auth import get_current_user, get_current_tenant_id, require_superadmin, hash_password

router = APIRouter(prefix="/api/tenants", tags=["Multi-Tenant SaaS & MDM (Master Data) / टेनेन्ट र मास्टर डाटा"])

# ============================================================================
# NEPAL LEGAL & CORPORATE MASTER DATA MANAGEMENT (MDM) DEFAULT CATALOG
# ============================================================================
DEFAULT_TENANT_LOVS: list[tuple[str, str, str, int]] = [
    # 1. COURT_NAME — अदालत तथा न्यायाधिकरणको सूची (Adalat List)
    ("COURT_NAME", "Supreme Court of Nepal", "सर्वोच्च अदालत", 1),
    ("COURT_NAME", "High Court Patan", "उच्च अदालत पाटन", 2),
    ("COURT_NAME", "High Court Biratnagar", "उच्च अदालत विराटनगर", 3),
    ("COURT_NAME", "High Court Janakpur (Rajbiraj / Birgunj Bench)", "उच्च अदालत जनकपुर (अस्थायी इजलास वीरगञ्ज)", 4),
    ("COURT_NAME", "High Court Pokhara", "उच्च अदालत पोखरा", 5),
    ("COURT_NAME", "High Court Tulsipur (Butwal / Nepalgunj Bench)", "उच्च अदालत तुलसीपुर (बुटवल इजलास)", 6),
    ("COURT_NAME", "High Court Surkhet", "उच्च अदालत सुर्खेत", 7),
    ("COURT_NAME", "High Court Dipayal (Mahendranagar Bench)", "उच्च अदालत दिपायल", 8),
    ("COURT_NAME", "Kathmandu District Court", "काठमाडौँ जिल्ला अदालत", 9),
    ("COURT_NAME", "Lalitpur District Court", "ललितपुर जिल्ला अदालत", 10),
    ("COURT_NAME", "Bhaktapur District Court", "भक्तपुर जिल्ला अदालत", 11),
    ("COURT_NAME", "Kaski District Court", "कास्की जिल्ला अदालत", 12),
    ("COURT_NAME", "Morang District Court", "मोरङ जिल्ला अदालत", 13),
    ("COURT_NAME", "Chitwan District Court", "चितवन जिल्ला अदालत", 14),
    ("COURT_NAME", "Rupandehi District Court", "रुपन्देही जिल्ला अदालत", 15),
    ("COURT_NAME", "Parsa District Court", "पर्सा जिल्ला अदालत", 16),
    ("COURT_NAME", "Special Court Kathmandu", "विशेष अदालत, काठमाडौँ", 17),
    ("COURT_NAME", "Revenue Tribunal Kathmandu", "राजस्व न्यायाधिकरण, काठमाडौँ", 18),
    ("COURT_NAME", "Labour Court Kathmandu", "श्रम अदालत, काठमाडौँ", 19),
    ("COURT_NAME", "Administrative Court", "प्रशासकीय अदालत, काठमाडौँ", 20),
    ("COURT_NAME", "Debt Recovery Tribunal (DRT)", "ऋण असुली न्यायाधिकरण", 21),
    ("COURT_NAME", "Foreign Employment Tribunal", "वैदेशिक रोजगार न्यायाधिकरण", 22),

    # 2. CASE_TYPE — मुद्दाको प्रकृति / प्रकार (Mudda ko Prakriti)
    ("CASE_TYPE", "Partition of Property", "अंशबण्डा", 1),
    ("CASE_TYPE", "Loan / Transaction Recovery", "लेनदेन तथा साँवा ब्याज भराई", 2),
    ("CASE_TYPE", "Divorce & Alimony", "सम्बन्ध विच्छेद र अंश मानाचामल", 3),
    ("CASE_TYPE", "Cheque Bounce (Negotiable Instruments)", "चेक अनादर (विनिमय अधिकारपत्र)", 4),
    ("CASE_TYPE", "Banking Offense", "बैंकिङ कसूर तथा सजाय", 5),
    ("CASE_TYPE", "Deed Cancellation & Fraud", "दूषित लिखत बदर र जालसाजी", 6),
    ("CASE_TYPE", "Land Dispute & Boundary Encroachment", "जग्गा खिचलो र साँध सिमाना", 7),
    ("CASE_TYPE", "Writ Petition - Certiorari / Mandamus / Habeas Corpus", "रिट निवेदन (उत्प्रेषण / परमादेश / बन्दीप्रत्यक्षीकरण)", 8),
    ("CASE_TYPE", "Corporate & Breach of Contract", "कर्पोरेट तथा करार उल्लंघन क्षतिपूर्ति", 9),
    ("CASE_TYPE", "Criminal Defense & Bail Hearing", "फौजदारी कसूर तथा थुनछेक बहस", 10),
    ("CASE_TYPE", "Tax & Revenue Assessment Appeal", "कर निर्धारण तथा राजस्व पुनरावेदन", 11),
    ("CASE_TYPE", "Labour & Employment Dispute", "श्रम तथा रोजगार विवाद", 12),
    ("CASE_TYPE", "Intellectual Property / Trademark / Copyright", "बौद्धिक सम्पत्ति, ट्रेडमार्क र प्रतिलिपि अधिकार", 13),
    ("CASE_TYPE", "Commercial Arbitration & Mediation", "वाणिज्य मध्यस्थता तथा मेलमिलाप", 14),
    ("CASE_TYPE", "House Rent & Eviction", "घरभाडा भराइ तथा घर खाली (निष्कासन)", 15),
    ("CASE_TYPE", "Defamation & Cyber Offense", "गाली बेइज्जती तथा विद्युतीय कारोबार कसूर", 16),

    # 3. HEARING_STATUS — पेशी तथा तारेखको अवस्था (Peshi / Tarekh Status)
    ("HEARING_STATUS", "Tarekh", "तारेख", 1),
    ("HEARING_STATUS", "General Tarekh", "साधारण तारेख", 2),
    ("HEARING_STATUS", "Scheduled for Arguments", "बहस / पेशी तोकिएको", 3),
    ("HEARING_STATUS", "Interim Order Hearing", "अन्तरिम आदेश छलफल", 4),
    ("HEARING_STATUS", "Court Order Issued", "आदेश भएको (कैफियत / झिकाउने)", 5),
    ("HEARING_STATUS", "Witness & Evidence Examination", "प्रमाण बुझ्ने / साक्षी बकपत्र", 6),
    ("HEARING_STATUS", "Postponed by Party/Counsel", "स्थगित (कानून व्यवसायी / पक्षबाट)", 7),
    ("HEARING_STATUS", "Not Reached by Bench", "हेर्न नभ्याइने", 8),
    ("HEARING_STATUS", "Part Heard (Herda-Herdai)", "हेर्दाहेर्दै", 9),
    ("HEARING_STATUS", "Sent to Mediation Center", "मेलमिलाप केन्द्रमा पठाइएको", 10),
    ("HEARING_STATUS", "Final Verdict / Decided", "फैसला", 11),

    # 4. CASE_STATUS — मुद्दाको समग्र अवस्था (Case Status)
    ("CASE_STATUS", "Active / In Tarekh", "तारेखमा / विचाराधीन (Active)", 1),
    ("CASE_STATUS", "In Arguments", "बहसको क्रममा (In Arguments)", 2),
    ("CASE_STATUS", "Process Service / Myad Tameli", "म्याद तामेलीको चरणमा", 3),
    ("CASE_STATUS", "Mediation / Settlement", "मिलापत्र प्रक्रियामा (In Mediation)", 4),
    ("CASE_STATUS", "Decided", "फैसला भएको (Decided)", 5),
    ("CASE_STATUS", "In Appeal", "पुनरावेदनमा गएको (Appealed)", 6),
    ("CASE_STATUS", "Judgment Execution", "फैसला कार्यान्वयनमा (Execution)", 7),

    # 5. PARTY_ROLE — पक्षको हैसियत (Client Party Role)
    ("PARTY_ROLE", "Plaintiff", "वादी", 1),
    ("PARTY_ROLE", "Defendant", "प्रतिवादी", 2),
    ("PARTY_ROLE", "Petitioner", "निवेदक / रिट निवेदक", 3),
    ("PARTY_ROLE", "Respondent", "विपक्षी", 4),
    ("PARTY_ROLE", "Appellant", "पुनरावेदक", 5),
    ("PARTY_ROLE", "Appellee", "प्रत्यर्थी", 6),
    ("PARTY_ROLE", "Complainant", "जाहेरवाला", 7),

    # 6. DOCUMENT_TYPE — कागजातको प्रकार (Document Format)
    ("DOCUMENT_TYPE", "Original", "मूल कागजात", 1),
    ("DOCUMENT_TYPE", "Copy", "प्रतिलिपि", 2),
    ("DOCUMENT_TYPE", "Certified Copy", "प्रमाणित प्रतिलिपि (नक्कल)", 3),
    ("DOCUMENT_TYPE", "Power of Attorney (Warisnama)", "अधिकृत वारेसनामा / साधारण वारेसनामा", 4),
    ("DOCUMENT_TYPE", "Court Pleading (Firad / Pratiuttar)", "फिरादपत्र / प्रतिउत्तरपत्र / पुनरावेदनपत्र", 5),

    # 7. PAYMENT_METHOD — भुक्तानीको माध्यम (Payment Methods)
    ("PAYMENT_METHOD", "Cash", "नगद", 1),
    ("PAYMENT_METHOD", "Bank Transfer", "बैंक ट्रान्सफर", 2),
    ("PAYMENT_METHOD", "Cheque", "चेक", 3),
    ("PAYMENT_METHOD", "eSewa", "eSewa", 4),
    ("PAYMENT_METHOD", "Khalti", "Khalti", 5),
    ("PAYMENT_METHOD", "ConnectIPS", "ConnectIPS", 6),

    # 8. COMPANY_TYPE — कम्पनीको प्रकार (Company Types - OCR)
    ("COMPANY_TYPE", "Private Limited (Pvt. Ltd.)", "प्राइभेट लिमिटेड (प्रा.लि.)", 1),
    ("COMPANY_TYPE", "Public Limited (Ltd.)", "पब्लिक लिमिटेड (लि.)", 2),
    ("COMPANY_TYPE", "Profit Not Distributing Company", "मुनाफा वितरण नगर्ने कम्पनी", 3),
    ("COMPANY_TYPE", "Foreign Company Branch / Liaison", "विदेशी कम्पनीको शाखा / सम्पर्क कार्यालय", 4),
    ("COMPANY_TYPE", "Partnership / Proprietorship Firm", "साझेदारी वा प्राइभेट फर्म (घरेलु / वाणिज्य)", 5),

    # 9. IRD_OFFICE — आन्तरिक राजस्व कार्यालयको सूची (IRD Tax Offices)
    ("IRD_OFFICE", "IRD Baneshwor", "आन्तरिक राजस्व कार्यालय, बानेश्वर", 1),
    ("IRD_OFFICE", "IRD Putalisadak", "आन्तरिक राजस्व कार्यालय, पुतलीसडक", 2),
    ("IRD_OFFICE", "IRD Tripureshwor", "आन्तरिक राजस्व कार्यालय, त्रिपुरेश्वर", 3),
    ("IRD_OFFICE", "IRD Lalitpur", "आन्तरिक राजस्व कार्यालय, ललितपुर", 4),
    ("IRD_OFFICE", "IRD Bhaktapur", "आन्तरिक राजस्व कार्यालय, भक्तपुर", 5),
    ("IRD_OFFICE", "IRD Kalanki", "आन्तरिक राजस्व कार्यालय, कलंकी", 6),
    ("IRD_OFFICE", "IRD Balaju", "आन्तरिक राजस्व कार्यालय, बालाजु", 7),
    ("IRD_OFFICE", "IRD Chabahil", "आन्तरिक राजस्व कार्यालय, चाबहिल", 8),
    ("IRD_OFFICE", "IRD Koteshwor", "आन्तरिक राजस्व कार्यालय, कोटेश्वर", 9),
    ("IRD_OFFICE", "Medium Taxpayers Office (MTO Babarmahal)", "मध्यमस्तरीय करदाता कार्यालय, बबरमहल", 10),
    ("IRD_OFFICE", "Large Taxpayers Office (LTO Hariharbhawan)", "ठूला करदाता कार्यालय, हरिहरभवन", 11),
    ("IRD_OFFICE", "IRD Pokhara", "आन्तरिक राजस्व कार्यालय, पोखरा", 12),
    ("IRD_OFFICE", "IRD Biratnagar", "आन्तरिक राजस्व कार्यालय, विराटनगर", 13),
    ("IRD_OFFICE", "IRD Birgunj", "आन्तरिक राजस्व कार्यालय, वीरगञ्ज", 14),
    ("IRD_OFFICE", "IRD Butwal", "आन्तरिक राजस्व कार्यालय, बुटवल", 15),
]

CATEGORY_ALIASES = {
    "COURT": "COURT_NAME",
    "COURT_NAME": "COURT_NAME",
    "ADALAT": "COURT_NAME",
    "CASE_TYPE": "CASE_TYPE",
    "MUDDA_PRAKRITI": "CASE_TYPE",
    "HEARING_STATUS": "HEARING_STATUS",
    "PESHI_STATUS": "HEARING_STATUS",
    "CASE_STATUS": "CASE_STATUS",
    "PARTY_ROLE": "PARTY_ROLE",
    "DOCUMENT_TYPE": "DOCUMENT_TYPE",
    "PAYMENT_METHOD": "PAYMENT_METHOD",
    "COMPANY_TYPE": "COMPANY_TYPE",
    "IRD_OFFICE": "IRD_OFFICE",
}


def normalize_category(cat: str) -> str:
    clean = (cat or "COURT_NAME").strip().upper()
    return CATEGORY_ALIASES.get(clean, clean)


def provision_tenant_defaults(tenant_or_id: Tenant | int, db: Session, force_missing_mdm: bool = False):
    """Create default SystemModuleConfig and MDM (TenantLOV) records for a tenant if missing."""
    if isinstance(tenant_or_id, int):
        tenant = db.query(Tenant).filter(Tenant.id == tenant_or_id).first()
        tid = tenant_or_id
    else:
        tenant = tenant_or_id
        tid = tenant.id

    existing_mods = db.query(SystemModuleConfig).filter(SystemModuleConfig.tenant_id == tid).count()
    if existing_mods == 0:
        db.add_all(
            [
                SystemModuleConfig(
                    tenant_id=tid,
                    module_key="legal",
                    name_en="Legal & Court Litigation Module",
                    name_np="मुद्दा तथा कानूनी व्यवस्थापन मोड्युल",
                    description_en="Court cases (Mudda), Daily Hearings (Peshi/Tarekh), Legal Documents, Conflict Check & Fee Receipts.",
                    description_np="अदालती मुद्दा, दैनिक पेशी/तारेख, कानूनी कागजात, विपक्षी द्वन्द्व जाँच र वकालत शुल्क रसिद व्यवस्थापन।",
                    is_enabled=tenant.enable_legal_module if tenant else True,
                    plan_tier=tenant.subscription_plan if tenant else "Enterprise",
                ),
                SystemModuleConfig(
                    tenant_id=tid,
                    module_key="company_management",
                    name_en="Company Management (OCR, IRD Tax & Audit) Module",
                    name_np="कम्पनी व्यवस्थापन (OCR, आन्तरिक राजस्व कर र लेखापरीक्षण) मोड्युल",
                    description_en="Plug-and-play module for Office of the Company Registrar (OCR) filings, IRD Tax returns & Tax Clearance, Statutory Audit (UDIN/AGM) & Periodic Compliance Reminders.",
                    description_np="कम्पनी रजिष्ट्रारको कार्यालय (OCR) दर्ता/अद्यावधिक, आन्तरिक राजस्व (IRD) भ्याट/आयकर/कर चुक्ता, लेखापरीक्षण (Audit/UDIN) र म्याद अनुस्मारक प्रणाली।",
                    is_enabled=tenant.enable_company_module if tenant else True,
                    enable_ocr=tenant.enable_ocr_sub if tenant else True,
                    enable_ird_tax=tenant.enable_ird_sub if tenant else True,
                    enable_audit=tenant.enable_audit_sub if tenant else True,
                    plan_tier=tenant.subscription_plan if tenant else "Enterprise",
                ),
            ]
        )

    existing_lovs = db.query(TenantLOV).filter(TenantLOV.tenant_id == tid).all()
    if not existing_lovs or force_missing_mdm:
        existing_pairs = {(x.category, x.value_en) for x in existing_lovs}
        new_lovs = []
        for cat, v_en, v_np, order in DEFAULT_TENANT_LOVS:
            if (cat, v_en) not in existing_pairs:
                new_lovs.append(
                    TenantLOV(
                        tenant_id=tid,
                        category=cat,
                        value_en=v_en,
                        value_np=v_np,
                        display_label=f"{v_np} ({v_en})" if v_np != v_en else v_en,
                        sort_order=order,
                        is_active=True,
                    )
                )
        if new_lovs:
            db.add_all(new_lovs)


def serialize_tenant(t: Tenant, db: Session) -> dict:
    users_count = db.query(StaffMember).filter(StaffMember.tenant_id == t.id).count()
    clients_count = db.query(Client).filter(Client.tenant_id == t.id).count()
    cases_count = db.query(LegalCase).filter(LegalCase.tenant_id == t.id).count()
    companies_count = db.query(CorporateEntity).filter(CorporateEntity.tenant_id == t.id).count()
    mods = db.query(SystemModuleConfig).filter(SystemModuleConfig.tenant_id == t.id).all()
    admin_user = (
        db.query(StaffMember)
        .filter(StaffMember.tenant_id == t.id, StaffMember.role.in_(["admin", "superadmin"]))
        .first()
    )
    return {
        "id": t.id,
        "tenant_code": t.tenant_code,
        "firm_name_en": t.firm_name_en,
        "firm_name_np": t.firm_name_np,
        "firm_type": t.firm_subtitle or "Law, Corporate & Audit Firm",
        "firm_subtitle": t.firm_subtitle or "",
        "pan_vat_no": t.pan_vat_no or "",
        "address": t.address,
        "phone": t.phone,
        "email": t.email or "",
        "receipt_prefix": t.receipt_prefix,
        "subscription_plan": t.subscription_plan,
        "subscription_status": t.subscription_status,
        "status": t.subscription_status or ("Active" if t.is_active else "Suspended"),
        "subscription_expiry_bs": t.subscription_expiry_bs or "",
        "max_users": t.max_users,
        "enable_legal_module": t.enable_legal_module,
        "enable_company_module": t.enable_company_module,
        "enable_ocr_sub": t.enable_ocr_sub,
        "enable_ird_sub": t.enable_ird_sub,
        "enable_audit_sub": t.enable_audit_sub,
        "is_active": t.is_active,
        "users_count": users_count,
        "clients_count": clients_count,
        "cases_count": cases_count,
        "companies_count": companies_count,
        "admin_username": admin_user.username if admin_user else "",
        "modules": [
            {"module_key": m.module_key, "name_en": m.name_en, "is_enabled": m.is_enabled}
            for m in mods
        ],
    }


def serialize_lov(lov: TenantLOV) -> dict:
    return {
        "id": lov.id,
        "tenant_id": lov.tenant_id,
        "category": lov.category,
        "lov_group": "COURT" if lov.category == "COURT_NAME" else lov.category,
        "value_en": lov.value_en,
        "value_np": lov.value_np,
        "label_en": lov.value_en,
        "label_np": lov.value_np,
        "display_label": lov.display_label,
        "sort_order": lov.sort_order,
        "is_active": lov.is_active,
    }


@router.get("/current")
def get_current_tenant_context(
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    provision_tenant_defaults(tenant, db, force_missing_mdm=False)
    db.commit()

    lovs = (
        db.query(TenantLOV)
        .filter(TenantLOV.tenant_id == tenant_id, TenantLOV.is_active == True)
        .order_by(TenantLOV.category.asc(), TenantLOV.sort_order.asc(), TenantLOV.id.asc())
        .all()
    )
    grouped_lovs: dict[str, list[dict]] = {}
    for item in lovs:
        s = serialize_lov(item)
        grouped_lovs.setdefault(item.category, []).append(s)
        if item.category == "COURT_NAME":
            grouped_lovs.setdefault("COURT", []).append(s)

    return {
        "tenant": serialize_tenant(tenant, db),
        "lovs": grouped_lovs,
        "lovs_by_group": grouped_lovs,
    }


@router.put("/current")
def update_current_tenant_profile(
    payload: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    allowed_fields = {
        "firm_name_en",
        "firm_name_np",
        "firm_subtitle",
        "pan_vat_no",
        "address",
        "phone",
        "email",
        "receipt_prefix",
    }
    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        if k in allowed_fields or current_user.is_superadmin:
            setattr(tenant, k, v)

    db.commit()
    db.refresh(tenant)
    return serialize_tenant(tenant, db)


# ============================================================
# TENANT-SCOPED MDM / LOV (MASTER DATA MANAGEMENT) ENDPOINTS
# ============================================================

@router.get("/lov")
def list_tenant_lovs(
    category: Optional[str] = Query(None),
    lov_group: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    query = db.query(TenantLOV).filter(TenantLOV.tenant_id == tenant_id)
    target_cat = category or lov_group
    if target_cat:
        norm = normalize_category(target_cat)
        query = query.filter(TenantLOV.category == norm)
    items = query.order_by(TenantLOV.category.asc(), TenantLOV.sort_order.asc(), TenantLOV.id.asc()).all()
    return [serialize_lov(i) for i in items]


@router.post("/lov")
def create_tenant_lov(
    payload: TenantLOVCreate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    raw_cat = payload.category or payload.lov_group or "COURT_NAME"
    norm_cat = normalize_category(raw_cat)
    v_en = (payload.value_en or payload.label_en or "").strip()
    v_np = (payload.value_np or payload.label_np or v_en).strip()
    if not v_en:
        raise HTTPException(status_code=400, detail="English label/value is required")

    display = f"{v_np} ({v_en})" if v_np != v_en else v_en
    lov = TenantLOV(
        tenant_id=tenant_id,
        category=norm_cat,
        value_en=v_en,
        value_np=v_np,
        display_label=display,
        sort_order=payload.sort_order,
        is_active=payload.is_active,
    )
    db.add(lov)
    db.commit()
    db.refresh(lov)
    return serialize_lov(lov)


@router.delete("/lov/{lov_id}")
def delete_tenant_lov(
    lov_id: int,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    lov = db.query(TenantLOV).filter(TenantLOV.id == lov_id, TenantLOV.tenant_id == tenant_id).first()
    if not lov:
        raise HTTPException(status_code=404, detail="MDM / LOV item not found in your tenant")
    db.delete(lov)
    db.commit()
    return {"message": "MDM / LOV item deleted"}


@router.post("/mdm/seed-defaults")
def seed_missing_mdm_defaults(
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Restore / seed any missing standard Nepal MDM values (Adalat List, Mudda ko Prakriti, Peshi Status, IRD Offices, etc.)."""
    provision_tenant_defaults(tenant_id, db, force_missing_mdm=True)
    db.commit()
    total = db.query(TenantLOV).filter(TenantLOV.tenant_id == tenant_id).count()
    return {
        "message": "Master Data Management (MDM) standard lists synced successfully",
        "total_mdm_items": total,
    }


@router.post("/clear-transactions")
def clear_tenant_transactional_data(
    scope: str = Query("tenant", description="'tenant' to clear current tenant, or 'all' (SuperAdmin) to clear all tenants"),
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    """Clear all transactional data (Hearings, Payments, Documents, Cases, Compliance Tasks, Companies, Clients)
    while preserving Tenants, Staff/Admin Accounts, Module Configs, and MDM Master Data (Adalat List, Mudda ko Prakriti, etc.).
    """
    if current_user.role not in ("admin", "superadmin") and not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Only Firm Admin or SuperAdmin can clear transactional data")

    if scope == "all" and current_user.is_superadmin:
        db.query(Hearing).delete(synchronize_session=False)
        db.query(PaymentRecord).delete(synchronize_session=False)
        db.query(CaseDocument).delete(synchronize_session=False)
        db.query(LegalCase).delete(synchronize_session=False)
        db.query(ComplianceActivity).delete(synchronize_session=False)
        db.query(CorporateEntity).delete(synchronize_session=False)
        db.query(Client).delete(synchronize_session=False)
    else:
        db.query(Hearing).filter(Hearing.tenant_id == tenant_id).delete(synchronize_session=False)
        db.query(PaymentRecord).filter(PaymentRecord.tenant_id == tenant_id).delete(synchronize_session=False)
        db.query(CaseDocument).filter(CaseDocument.tenant_id == tenant_id).delete(synchronize_session=False)
        db.query(LegalCase).filter(LegalCase.tenant_id == tenant_id).delete(synchronize_session=False)
        db.query(ComplianceActivity).filter(ComplianceActivity.tenant_id == tenant_id).delete(synchronize_session=False)
        db.query(CorporateEntity).filter(CorporateEntity.tenant_id == tenant_id).delete(synchronize_session=False)
        db.query(Client).filter(Client.tenant_id == tenant_id).delete(synchronize_session=False)

    # Ensure MDM master data is intact
    provision_tenant_defaults(tenant_id, db, force_missing_mdm=True)
    db.commit()
    return {
        "status": "cleared",
        "scope": scope,
        "tenant_id": tenant_id,
        "message": "All transactional records cleared; Master Data (MDM), Users, and Tenant Settings preserved.",
    }


# ============================================================
# SAAS PLATFORM HOST (SUPERADMIN) TENANT MANAGEMENT ENDPOINTS
# ============================================================

@router.get("")
def list_all_tenants(
    db: Session = Depends(get_db),
    superadmin: StaffMember = Depends(require_superadmin),
):
    tenants = db.query(Tenant).order_by(Tenant.id.asc()).all()
    return [serialize_tenant(t, db) for t in tenants]


@router.post("")
def create_new_saas_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    superadmin: StaffMember = Depends(require_superadmin),
):
    if db.query(Tenant).filter(Tenant.tenant_code == payload.tenant_code.strip().upper()).first():
        raise HTTPException(status_code=400, detail="Tenant code already exists")
    if db.query(StaffMember).filter(StaffMember.username == payload.admin_username.strip()).first():
        raise HTTPException(status_code=400, detail="Admin username is already taken across the platform")

    tenant = Tenant(
        tenant_code=payload.tenant_code.strip().upper(),
        firm_name_en=payload.firm_name_en.strip(),
        firm_name_np=(payload.firm_name_np or payload.firm_name_en).strip(),
        firm_subtitle=payload.firm_subtitle,
        pan_vat_no=payload.pan_vat_no,
        address=(payload.address or "Kathmandu, Nepal").strip(),
        phone=payload.phone.strip(),
        email=payload.email,
        receipt_prefix=(payload.receipt_prefix or "RCP").strip().upper(),
        subscription_plan=payload.subscription_plan,
        subscription_status=payload.subscription_status,
        subscription_expiry_bs=payload.subscription_expiry_bs,
        max_users=payload.max_users,
        enable_legal_module=payload.enable_legal_module,
        enable_company_module=payload.enable_company_module,
        enable_ocr_sub=payload.enable_ocr_sub,
        enable_ird_sub=payload.enable_ird_sub,
        enable_audit_sub=payload.enable_audit_sub,
        is_active=True,
    )
    db.add(tenant)
    db.flush()

    # Provision tenant-isolated Module Configs & Default MDM / LOVs
    provision_tenant_defaults(tenant, db, force_missing_mdm=True)

    # Create the Tenant's Admin User (Login resolves directly to this tenant_id!)
    admin_user = StaffMember(
        tenant_id=tenant.id,
        is_superadmin=False,
        full_name=payload.admin_full_name.strip(),
        role="admin",
        designation="प्रबन्ध साझेदार / प्रमुख (Managing Partner)",
        phone=payload.admin_phone or payload.phone.strip(),
        email=payload.email,
        address=tenant.address,
        username=payload.admin_username.strip(),
        password_hash=hash_password(payload.admin_password),
        is_active=True,
        notes=f"Primary Admin for Tenant {tenant.tenant_code}",
    )
    db.add(admin_user)
    db.commit()
    db.refresh(tenant)
    return serialize_tenant(tenant, db)


@router.put("/{target_tenant_id}")
def update_saas_tenant(
    target_tenant_id: int,
    payload: TenantUpdate,
    db: Session = Depends(get_db),
    superadmin: StaffMember = Depends(require_superadmin),
):
    tenant = db.query(Tenant).filter(Tenant.id == target_tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(tenant, k, v)

    legal_mod = (
        db.query(SystemModuleConfig)
        .filter(SystemModuleConfig.tenant_id == tenant.id, SystemModuleConfig.module_key == "legal")
        .first()
    )
    if legal_mod and "enable_legal_module" in update_data:
        legal_mod.is_enabled = tenant.enable_legal_module

    comp_mod = (
        db.query(SystemModuleConfig)
        .filter(SystemModuleConfig.tenant_id == tenant.id, SystemModuleConfig.module_key == "company_management")
        .first()
    )
    if comp_mod:
        if "enable_company_module" in update_data:
            comp_mod.is_enabled = tenant.enable_company_module
        if "enable_ocr_sub" in update_data:
            comp_mod.enable_ocr = tenant.enable_ocr_sub
        if "enable_ird_sub" in update_data:
            comp_mod.enable_ird_tax = tenant.enable_ird_sub
        if "enable_audit_sub" in update_data:
            comp_mod.enable_audit = tenant.enable_audit_sub

    db.commit()
    db.refresh(tenant)
    return serialize_tenant(tenant, db)
