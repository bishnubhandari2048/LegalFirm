from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.database import Base


# ============================================================================
# 0. ENTERPRISE MULTI-TENANT CORE (TENANTS & TENANT-SCOPED LOV / SETTINGS)
# ============================================================================

class Tenant(Base):
    """SaaS Tenant (Law Firm / Corporate Secretarial Firm / Audit Firm)."""

    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    tenant_code = Column(String(50), nullable=False, unique=True, index=True)  # e.g. TENANT-001
    firm_name_en = Column(String(200), nullable=False)
    firm_name_np = Column(String(200), nullable=False)
    firm_subtitle = Column(String(200), nullable=True, default="Advocates, Corporate Consultants & Tax Advisors")
    pan_vat_no = Column(String(60), nullable=True)
    address = Column(String(255), nullable=False)
    phone = Column(String(60), nullable=False)
    email = Column(String(120), nullable=True)
    receipt_prefix = Column(String(20), nullable=False, default="RCP")

    # Subscription & Module Entitlements (Managed by SaaS Host / SuperAdmin)
    subscription_plan = Column(String(60), nullable=False, default="Enterprise")  # Basic, Professional, Enterprise
    subscription_status = Column(String(40), nullable=False, default="Active")    # Active, Trial, Suspended
    subscription_expiry_bs = Column(String(30), nullable=True, default="2084-12-30")
    max_users = Column(Integer, default=25)

    enable_legal_module = Column(Boolean, default=True, nullable=False)
    enable_company_module = Column(Boolean, default=True, nullable=False)
    enable_ocr_sub = Column(Boolean, default=True, nullable=False)
    enable_ird_sub = Column(Boolean, default=True, nullable=False)
    enable_audit_sub = Column(Boolean, default=True, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class TenantLOV(Base):
    """Tenant-Scoped List of Values (LOV) for Courts, Case Types, Hearing Statuses, Payment Methods, IRD Offices, etc."""

    __tablename__ = "tenant_lovs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(60), nullable=False, index=True)
    # Categories: COURT_NAME, CASE_TYPE, HEARING_STATUS, PAYMENT_METHOD, DOCUMENT_TYPE, IRD_OFFICE, COMPANY_TYPE
    value_en = Column(String(200), nullable=False)
    value_np = Column(String(200), nullable=False)
    display_label = Column(String(250), nullable=False)
    sort_order = Column(Integer, default=10)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemModuleConfig(Base):
    """Tenant-Scoped Plug-and-Play Module Subscription & Feature Flag Configuration."""

    __tablename__ = "system_module_configs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, default=1, index=True)
    module_key = Column(String(60), nullable=False, index=True)  # 'legal', 'company_management'
    name_en = Column(String(150), nullable=False)
    name_np = Column(String(150), nullable=False)
    description_en = Column(Text, nullable=True)
    description_np = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True, nullable=False)
    enable_ocr = Column(Boolean, default=True, nullable=False)
    enable_ird_tax = Column(Boolean, default=True, nullable=False)
    enable_audit = Column(Boolean, default=True, nullable=False)
    plan_tier = Column(String(60), default="Enterprise")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StaffMember(Base):
    """वकिल, लेखापरीक्षक तथा कर्मचारी विवरण (Tenant-Scoped Users + SaaS SuperAdmin)."""

    __tablename__ = "staff_members"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, default=1, index=True)
    is_superadmin = Column(Boolean, default=False, nullable=False)  # True for SaaS Platform Host Owner

    full_name = Column(String(150), nullable=False, index=True)
    role = Column(String(40), nullable=False, default="advocate")  # superadmin, admin, advocate, auditor, staff
    designation = Column(String(100), nullable=False, default="अधिवक्ता (Advocate)")
    bar_council_no = Column(String(60), nullable=True)
    specialization = Column(String(150), nullable=True)
    phone = Column(String(40), nullable=False)
    alt_phone = Column(String(40), nullable=True)
    email = Column(String(120), nullable=True)
    address = Column(String(255), nullable=True)
    username = Column(String(80), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", foreign_keys=[tenant_id])
    lead_cases = relationship("LegalCase", back_populates="advocate", foreign_keys="LegalCase.advocate_id")
    assisted_cases = relationship("LegalCase", back_populates="assistant", foreign_keys="LegalCase.assistant_id")


class Client(Base):
    """क्लाइन्टको विवरण (Tenant-Scoped Client Information Records)."""

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, default=1, index=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), nullable=False, index=True)
    address = Column(String(255), nullable=False)
    district = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=False, index=True)
    alt_phone = Column(String(50), nullable=True)
    email = Column(String(120), nullable=True)
    citizenship_no = Column(String(80), nullable=False, index=True)
    citizenship_district = Column(String(100), nullable=True)
    citizenship_issue_date_bs = Column(String(30), nullable=True)
    father_or_spouse_name = Column(String(150), nullable=True)
    occupation = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cases = relationship("LegalCase", back_populates="client", cascade="all, delete-orphan")
    payments = relationship("PaymentRecord", back_populates="client")
    documents = relationship("CaseDocument", back_populates="client")
    companies = relationship("CorporateEntity", back_populates="client")


class LegalCase(Base):
    """मुद्दाको विवरण (Tenant-Scoped Case Details)."""

    __tablename__ = "legal_cases"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, default=1, index=True)

    case_number = Column(String(100), nullable=False, index=True)
    filing_number = Column(String(100), nullable=True)
    case_title = Column(String(255), nullable=True)
    court_name = Column(String(200), nullable=False, index=True)
    bench_section = Column(String(100), nullable=True)
    case_type = Column(String(120), nullable=False, index=True)

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    client_party_role = Column(String(60), nullable=False, default="वादी (Plaintiff)")

    opponent_name = Column(String(200), nullable=False, index=True)
    opponent_address = Column(String(255), nullable=True)
    opponent_contact = Column(String(100), nullable=True)
    opponent_counsel = Column(String(150), nullable=True)

    registration_date_bs = Column(String(30), nullable=False)
    registration_date_ad = Column(Date, nullable=True)

    status = Column(String(80), nullable=False, default="विचाराधीन (Active)")

    deal_amount = Column(Float, nullable=False, default=0.0)
    paid_amount = Column(Float, nullable=False, default=0.0)
    due_amount = Column(Float, nullable=False, default=0.0)

    advocate_id = Column(Integer, ForeignKey("staff_members.id", ondelete="SET NULL"), nullable=True)
    assistant_id = Column(Integer, ForeignKey("staff_members.id", ondelete="SET NULL"), nullable=True)
    waris_name = Column(String(150), nullable=True)

    next_hearing_date_bs = Column(String(30), nullable=True, index=True)
    next_hearing_date_ad = Column(Date, nullable=True, index=True)

    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client = relationship("Client", back_populates="cases")
    advocate = relationship("StaffMember", back_populates="lead_cases", foreign_keys=[advocate_id])
    assistant = relationship("StaffMember", back_populates="assisted_cases", foreign_keys=[assistant_id])
    hearings = relationship("Hearing", back_populates="legal_case", cascade="all, delete-orphan", order_by="desc(Hearing.hearing_date_bs)")
    payments = relationship("PaymentRecord", back_populates="legal_case", cascade="all, delete-orphan", order_by="desc(PaymentRecord.id)")
    documents = relationship("CaseDocument", back_populates="legal_case", cascade="all, delete-orphan", order_by="desc(CaseDocument.id)")


class Hearing(Base):
    """पेशी विवरण (Tenant-Scoped Court Hearings / Peshi & Tarekh Records)."""

    __tablename__ = "hearings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, default=1, index=True)
    case_id = Column(Integer, ForeignKey("legal_cases.id", ondelete="CASCADE"), nullable=False, index=True)

    hearing_date_bs = Column(String(30), nullable=False, index=True)
    hearing_date_ad = Column(Date, nullable=True, index=True)
    hearing_status = Column(String(100), nullable=False)
    bench_or_judge = Column(String(150), nullable=True)
    next_hearing_date_bs = Column(String(30), nullable=True)
    next_hearing_date_ad = Column(Date, nullable=True)
    outcome = Column(Text, nullable=True)
    attended_by_id = Column(Integer, ForeignKey("staff_members.id", ondelete="SET NULL"), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    legal_case = relationship("LegalCase", back_populates="hearings")
    attended_by = relationship("StaffMember", foreign_keys=[attended_by_id])


class PaymentRecord(Base):
    """आर्थिक विवरण र भुक्तानी रसिद (Tenant-Scoped Financial Payments & Receipts)."""

    __tablename__ = "payment_records"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, default=1, index=True)
    case_id = Column(Integer, ForeignKey("legal_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)

    amount = Column(Float, nullable=False)
    payment_date_bs = Column(String(30), nullable=False, index=True)
    payment_date_ad = Column(Date, nullable=True)
    payment_method = Column(String(80), nullable=False, default="नगद (Cash)")
    receipt_number = Column(String(80), nullable=False, index=True)
    purpose = Column(String(120), nullable=False, default="वकालत शुल्क (Legal Fee)")
    reference_no = Column(String(120), nullable=True)
    remarks = Column(Text, nullable=True)
    received_by_id = Column(Integer, ForeignKey("staff_members.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    legal_case = relationship("LegalCase", back_populates="payments")
    client = relationship("Client", back_populates="payments")
    received_by = relationship("StaffMember", foreign_keys=[received_by_id])


class CaseDocument(Base):
    """कागजात सम्बन्धी विवरण (Tenant-Scoped Document Checklist & Handover)."""

    __tablename__ = "case_documents"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, default=1, index=True)
    case_id = Column(Integer, ForeignKey("legal_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=True, index=True)

    document_name = Column(String(200), nullable=False, index=True)
    document_type = Column(String(80), nullable=False, default="प्रतिलिपि (Copy)")
    status = Column(String(80), nullable=False, default="कार्यालयमा सुरक्षित (In Office)")
    received_date_bs = Column(String(30), nullable=False)
    received_date_ad = Column(Date, nullable=True)
    returned_date_bs = Column(String(30), nullable=True)
    returned_date_ad = Column(Date, nullable=True)
    handover_person = Column(String(150), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    legal_case = relationship("LegalCase", back_populates="documents")
    client = relationship("Client", back_populates="documents")


class CorporateEntity(Base):
    """कम्पनी व्यवस्थापन विवरण (Tenant-Scoped Registered Companies for OCR, IRD Tax & Audit)."""

    __tablename__ = "corporate_entities"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, default=1, index=True)

    company_name_en = Column(String(200), nullable=False, index=True)
    company_name_np = Column(String(200), nullable=True, index=True)
    company_type = Column(String(100), nullable=False, default="Private Limited (प्रा.लि.)")

    ocr_registration_no = Column(String(80), nullable=False, index=True)
    registration_date_bs = Column(String(30), nullable=False)
    registration_date_ad = Column(Date, nullable=True)
    camis_username = Column(String(100), nullable=True)

    pan_vat_no = Column(String(60), nullable=False, index=True)
    tax_registration_type = Column(String(40), nullable=False, default="VAT (मु.अ.कर)")
    ird_office = Column(String(150), nullable=False, default="आन्तरिक राजस्व कार्यालय, बानेश्वर")
    tax_clearance_upto_fy = Column(String(30), nullable=True, default="2081/82")

    authorized_capital = Column(Float, default=0.0)
    issued_capital = Column(Float, default=0.0)
    paidup_capital = Column(Float, default=0.0)
    shareholders_count = Column(Integer, default=1)
    directors_summary = Column(Text, nullable=True)
    registered_address = Column(String(255), nullable=False)
    contact_person = Column(String(150), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    contact_email = Column(String(120), nullable=True)

    current_auditor_name = Column(String(150), nullable=True)
    auditor_ican_no = Column(String(60), nullable=True)
    last_agm_date_bs = Column(String(30), nullable=True)
    last_ocr_filed_fy = Column(String(30), nullable=True, default="2081/82")

    annual_retainer_fee = Column(Float, default=0.0)
    paid_retainer_amount = Column(Float, default=0.0)
    due_retainer_amount = Column(Float, default=0.0)

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    assigned_officer_id = Column(Integer, ForeignKey("staff_members.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(60), default="Active (सक्रिय)")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    client = relationship("Client", back_populates="companies")
    assigned_officer = relationship("StaffMember", foreign_keys=[assigned_officer_id])
    activities = relationship(
        "ComplianceActivity",
        back_populates="company",
        cascade="all, delete-orphan",
        order_by="asc(ComplianceActivity.due_date_bs)",
    )


class ComplianceActivity(Base):
    """Tenant-Scoped OCR, IRD Tax & Audit Periodic Activities, Filings, Clearances & Reminders."""

    __tablename__ = "compliance_activities"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, default=1, index=True)
    company_id = Column(Integer, ForeignKey("corporate_entities.id", ondelete="CASCADE"), nullable=False, index=True)

    category = Column(String(40), nullable=False, index=True, default="OCR")
    activity_type = Column(String(160), nullable=False, index=True)
    fiscal_year = Column(String(30), nullable=False, default="2082/83", index=True)
    period_label = Column(String(80), nullable=True)

    due_date_bs = Column(String(30), nullable=False, index=True)
    due_date_ad = Column(Date, nullable=True, index=True)
    completed_date_bs = Column(String(30), nullable=True)
    next_reminder_date_bs = Column(String(30), nullable=True, index=True)

    status = Column(String(60), nullable=False, default="Pending (बाँकी)")
    priority = Column(String(40), nullable=False, default="High")

    reference_or_certificate_no = Column(String(120), nullable=True)
    auditor_or_officer_name = Column(String(150), nullable=True)
    udin_number = Column(String(80), nullable=True)

    gov_fee_or_penalty = Column(Float, default=0.0)
    professional_fee = Column(Float, default=0.0)

    assigned_to_id = Column(Integer, ForeignKey("staff_members.id", ondelete="SET NULL"), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("CorporateEntity", back_populates="activities")
    assigned_to = relationship("StaffMember", foreign_keys=[assigned_to_id])
