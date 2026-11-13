import logging
from sqlalchemy.orm import Session
from app.models import (
    Tenant,
    StaffMember,
)
from app.auth import hash_password
from app.routers.tenants_router import provision_tenant_defaults

logger = logging.getLogger("vidhicms.seed")


def ensure_multitenant_foundation(db: Session):
    """Ensure Tenant #1, Tenant #2 (Client Tenant), Admin Users, Module Configs,
    and Master Data Management (MDM: Adalat List, Mudda ko Prakriti, Peshi Status, IRD Offices, etc.) exist.
    Does NOT re-insert demo transactional data once cleared.
    """
    t1 = db.query(Tenant).filter(Tenant.id == 1).first()
    if not t1:
        t1 = Tenant(
            id=1,
            tenant_code="VIDHI-001",
            firm_name_en="Vidhi Law Firm & Corporate Consultancy",
            firm_name_np="विधि ल फर्म एण्ड कर्पोरेट कन्सल्टेन्सी",
            firm_subtitle="Advocates, Corporate Consultants (OCR), Tax & Audit Advisors",
            pan_vat_no="609112233",
            address="अनामनगर, काठमाडौँ (Anamnagar, Kathmandu)",
            phone="01-4523890 / 9851023456",
            email="info@vidhilaw.com.np",
            receipt_prefix="VIDHI-RCP",
            subscription_plan="Enterprise",
            subscription_status="Active",
            max_users=50,
            enable_legal_module=True,
            enable_company_module=True,
            enable_ocr_sub=True,
            enable_ird_sub=True,
            enable_audit_sub=True,
            is_active=True,
        )
        db.add(t1)
        db.flush()

    provision_tenant_defaults(t1, db, force_missing_mdm=True)

    # Ensure primary admin exists and is marked as SaaS Host SuperAdmin
    admin_user = db.query(StaffMember).filter(StaffMember.username == "admin").first()
    if not admin_user:
        admin_user = StaffMember(
            tenant_id=t1.id,
            full_name="वरिष्ठ अधिवक्ता रमेश प्रसाद शर्मा (Sr. Adv. Ramesh P. Sharma)",
            role="admin",
            is_superadmin=True,
            designation="वरिष्ठ अधिवक्ता / प्रबन्ध साझेदार (Managing Partner)",
            bar_council_no="NBC-1452",
            specialization="संवैधानिक, देवानी, कर्पोरेट र सर्वोच्च अदालत रिट (Constitutional & Corporate)",
            phone="9851023456",
            alt_phone="01-4523890",
            email="ramesh.sharma@vidhilaw.com.np",
            address="अनामनगर, काठमाडौँ (Anamnagar, Kathmandu)",
            username="admin",
            password_hash=hash_password("admin123"),
            is_active=True,
            notes="प्रमुख वरिष्ठ अधिवक्ता तथा कार्यालय प्रमुख (SaaS Host SuperAdmin)",
        )
        db.add(admin_user)
        db.flush()
    else:
        admin_user.is_superadmin = True
        admin_user.tenant_id = t1.id

    # Ensure 2nd isolated Tenant ("Apex Law & Tax Associates") exists with its own Admin & MDM
    t2 = db.query(Tenant).filter(Tenant.tenant_code == "APEX-002").first()
    if not t2:
        t2 = Tenant(
            tenant_code="APEX-002",
            firm_name_en="Apex Corporate, Tax & Legal Associates",
            firm_name_np="एपेक्स कर्पोरेट, कर तथा लिगल एसोसिएट्स",
            firm_subtitle="Corporate Secretarial (OCR), IRD Tax & Litigation Firm",
            pan_vat_no="610445566",
            address="पुतलीसडक, काठमाडौँ (Putalisadak, Kathmandu)",
            phone="01-4411223 / 9801887766",
            email="contact@apexlawnepal.com",
            receipt_prefix="APEX-RCP",
            subscription_plan="Enterprise",
            subscription_status="Active",
            max_users=25,
            enable_legal_module=True,
            enable_company_module=True,
            enable_ocr_sub=True,
            enable_ird_sub=True,
            enable_audit_sub=True,
            is_active=True,
        )
        db.add(t2)
        db.flush()

    provision_tenant_defaults(t2, db, force_missing_mdm=True)

    apex_admin = db.query(StaffMember).filter(StaffMember.username == "apex_admin").first()
    if not apex_admin:
        apex_admin = StaffMember(
            tenant_id=t2.id,
            full_name="अधिवक्ता / CA सुवासचन्द्र कोइराला (Adv. Subash Koirala)",
            role="admin",
            is_superadmin=False,
            designation="प्रबन्ध साझेदार (Managing Partner - Apex)",
            bar_council_no="NBC-7741 / ICAN-0912",
            specialization="कर्पोरेट कानून, उच्च अदालत रिट र कर लेखापरीक्षण",
            phone="9801887766",
            email="subash@apexlawnepal.com",
            address="पुतलीसडक, काठमाडौँ",
            username="apex_admin",
            password_hash=hash_password("lawfirm123"),
            is_active=True,
            notes="Tenant #2 (APEX-002) Primary Admin Account",
        )
        db.add(apex_admin)

    db.commit()


def seed_initial_data(db: Session):
    """Ensure Multi-Tenant Foundation, Admin Accounts, Plug-and-Play Modules,
    and Master Data Management (MDM: Adalat List, Mudda ko Prakriti, Peshi Status, IRD Offices) exist.
    Transactional tables remain clean after clearing.
    """
    ensure_multitenant_foundation(db)
