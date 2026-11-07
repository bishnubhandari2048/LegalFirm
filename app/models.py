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


class SystemModuleConfig(Base):
    """Plug-and-Play Module Subscription & Feature Flag Configuration."""

    __tablename__ = "system_module_configs"

    id = Column(Integer, primary_key=True, index=True)
    module_key = Column(String(60), nullable=False, unique=True, index=True)  # e.g. 'legal', 'company_management'
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
    """वकिल, लेखापरीक्षक तथा कर्मचारी विवरण (Advocates, Auditors, Paralegals & Admin Users)."""

    __tablename__ = "staff_members"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False, index=True)
    role = Column(String(40), nullable=False, default="advocate")  # admin, advocate, auditor, staff
    designation = Column(String(100), nullable=False, default="अधिवक्ता (Advocate)")
    bar_council_no = Column(String(60), nullable=True)  # नेपाल बार काउन्सिल वा ICAN दर्ता नं.
    specialization = Column(String(150), nullable=True)  # देवानी, कर्पोरेट, कर तथा लेखापरीक्षण आदि
    phone = Column(String(40), nullable=False)
    alt_phone = Column(String(40), nullable=True)
    email = Column(String(120), nullable=True, unique=True)
    address = Column(String(255), nullable=True)
    username = Column(String(80), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lead_cases = relationship("LegalCase", back_populates="advocate", foreign_keys="LegalCase.advocate_id")
    assisted_cases = relationship("LegalCase", back_populates="assistant", foreign_keys="LegalCase.assistant_id")


class Client(Base):
    """क्लाइन्टको विवरण (Client Information Records)."""

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)  # नाम
    last_name = Column(String(100), nullable=False)   # थर
    full_name = Column(String(200), nullable=False, index=True)  # नाम, थर
    address = Column(String(255), nullable=False)     # ठेगाना
    district = Column(String(100), nullable=True)     # जिल्ला
    phone = Column(String(50), nullable=False, index=True)  # सम्पर्क नम्बर
    alt_phone = Column(String(50), nullable=True)     # वैकल्पिक सम्पर्क नम्बर
    email = Column(String(120), nullable=True)        # इमेल (भएमा)
    citizenship_no = Column(String(80), nullable=False, index=True)  # नागरिकता नम्बर
    citizenship_district = Column(String(100), nullable=True)        # जारी जिल्ला
    citizenship_issue_date_bs = Column(String(30), nullable=True)    # जारी मिति (वि.सं.)
    father_or_spouse_name = Column(String(150), nullable=True)       # बाबु/पति/पत्नीको नाम
    occupation = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cases = relationship("LegalCase", back_populates="client", cascade="all, delete-orphan")
    payments = relationship("PaymentRecord", back_populates="client")
    documents = relationship("CaseDocument", back_populates="client")
    companies = relationship("CorporateEntity", back_populates="client")


class LegalCase(Base):
    """मुद्दाको विवरण (Case Details, Assigned Counsel & Financial Agreement Summary)."""

    __tablename__ = "legal_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(100), nullable=False, unique=True, index=True)  # मुद्दा नम्बर (Case No.)
    filing_number = Column(String(100), nullable=True)  # दर्ता / दायर नम्बर
    case_title = Column(String(255), nullable=True)     # मुद्दाको शीर्षक
    court_name = Column(String(200), nullable=False, index=True)  # अदालतको नाम
    bench_section = Column(String(100), nullable=True)  # फाँट वा इजलास
    case_type = Column(String(120), nullable=False, index=True)   # मुद्दाको प्रकार

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    client_party_role = Column(String(60), nullable=False, default="वादी (Plaintiff)")

    opponent_name = Column(String(200), nullable=False, index=True)  # विपक्षीको नाम
    opponent_address = Column(String(255), nullable=True)
    opponent_contact = Column(String(100), nullable=True)
    opponent_counsel = Column(String(150), nullable=True)

    registration_date_bs = Column(String(30), nullable=False)
    registration_date_ad = Column(Date, nullable=True)

    status = Column(String(80), nullable=False, default="विचाराधीन (Active)")

    # आर्थिक विवरण सारांश (Financial Deal Summary)
    deal_amount = Column(Float, nullable=False, default=0.0)
    paid_amount = Column(Float, nullable=False, default=0.0)
    due_amount = Column(Float, nullable=False, default=0.0)

    # वकिल तथा कर्मचारी विवरण (Assigned Advocate & Assistant Staff)
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
    """पेशी विवरण (Court Hearings / Peshi & Tarekh Records)."""

    __tablename__ = "hearings"

    id = Column(Integer, primary_key=True, index=True)
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
    """आर्थिक विवरण र भुक्तानी रसिद (Financial Payments, Installments & Receipts)."""

    __tablename__ = "payment_records"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("legal_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)

    amount = Column(Float, nullable=False)
    payment_date_bs = Column(String(30), nullable=False, index=True)
    payment_date_ad = Column(Date, nullable=True)
    payment_method = Column(String(80), nullable=False, default="नगद (Cash)")
    receipt_number = Column(String(80), nullable=False, unique=True, index=True)
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
    """कागजात सम्बन्धी विवरण (Document Checklist, Original vs Copy, Handover & Return Dates)."""

    __tablename__ = "case_documents"

    id = Column(Integer, primary_key=True, index=True)
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


# ============================================================================
# COMPANY MANAGEMENT MODULE (OCR + IRD TAX + STATUTORY AUDIT)
# ============================================================================

class CorporateEntity(Base):
    """कम्पनी व्यवस्थापन विवरण (Registered Companies / Firms for OCR, IRD Tax & Audit)."""

    __tablename__ = "corporate_entities"

    id = Column(Integer, primary_key=True, index=True)
    company_name_en = Column(String(200), nullable=False, index=True)
    company_name_np = Column(String(200), nullable=True, index=True)
    company_type = Column(String(100), nullable=False, default="Private Limited (प्रा.लि.)")
    # e.g. Private Limited (प्रा.लि.), Public Limited (लि.), Non-Profit (मुनाफा वितरण नगर्ने), Partnership, Proprietorship

    # OCR Details
    ocr_registration_no = Column(String(80), nullable=False, unique=True, index=True)
    registration_date_bs = Column(String(30), nullable=False)
    registration_date_ad = Column(Date, nullable=True)
    camis_username = Column(String(100), nullable=True)

    # IRD / Tax Details
    pan_vat_no = Column(String(60), nullable=False, index=True)
    tax_registration_type = Column(String(40), nullable=False, default="VAT (मु.अ.कर)")  # PAN Only, VAT (मु.अ.कर), Excise
    ird_office = Column(String(150), nullable=False, default="आन्तरिक राजस्व कार्यालय, बानेश्वर")
    tax_clearance_upto_fy = Column(String(30), nullable=True, default="2081/82")  # पछिल्लो कर चुक्ता आ.व.

    # Capital & Governance
    authorized_capital = Column(Float, default=0.0)  # अधिकृत पूँजी
    issued_capital = Column(Float, default=0.0)      # जारी पूँजी
    paidup_capital = Column(Float, default=0.0)      # चुक्ता पूँजी
    shareholders_count = Column(Integer, default=1)
    directors_summary = Column(Text, nullable=True)  # सञ्चालक तथा मुख्य शेयरधनीहरूको नाम
    registered_address = Column(String(255), nullable=False)
    contact_person = Column(String(150), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    contact_email = Column(String(120), nullable=True)

    # Statutory Auditor Info (Current FY)
    current_auditor_name = Column(String(150), nullable=True)
    auditor_ican_no = Column(String(60), nullable=True)
    last_agm_date_bs = Column(String(30), nullable=True)
    last_ocr_filed_fy = Column(String(30), nullable=True, default="2081/82")

    # Retainer / Consultancy Financials
    annual_retainer_fee = Column(Float, default=0.0)
    paid_retainer_amount = Column(Float, default=0.0)
    due_retainer_amount = Column(Float, default=0.0)

    # Links
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
    """OCR, IRD Tax & Audit Periodic Activities, Filings, Clearances & Reminders."""

    __tablename__ = "compliance_activities"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("corporate_entities.id", ondelete="CASCADE"), nullable=False, index=True)

    # Category: 'OCR', 'IRD_TAX', 'AUDIT'
    category = Column(String(40), nullable=False, index=True, default="OCR")
    activity_type = Column(String(160), nullable=False, index=True)
    # Examples:
    # OCR: 'New Company Registration (नयाँ कम्पनी दर्ता)', 'Section 78 Annual Return (दफा ७८ वार्षिक विवरण)',
    #      'Section 51 Share Lagat (दफा ५१ शेयर लगत)', 'Share Transfer (शेयर खरिद-बिक्री नामसारी)',
    #      'BOD Update (सञ्चालक लगत अद्यावधिक)', 'Capital/Objective Amendment (पूँजी/उद्देश्य संशोधन - ३ महले)',
    #      'Auditor Appointment Filing (लेखापरीक्षक नियुक्ति जानकारी)'
    # IRD_TAX: 'Monthly VAT Return (मासिक मु.अ.कर विवरण)', 'Monthly e-TDS Filing (अग्रिम कर कट्टी ई-टीडीएस)',
    #          'Estimated Tax 1st Installment - Poush (अनुमानित आयकर प्रथम किस्ता - पुस)',
    #          'Estimated Tax 2nd Installment - Chaitra (दोस्रो किस्ता - चैत)',
    #          'Estimated Tax 3rd Installment - Ashadh (तेस्रो किस्ता - असार)',
    #          'Annual Income Tax Return D-03 (वार्षिक आयकर विवरण D-01/D-03)',
    #          'Tax Clearance Certificate (कर चुक्ता प्रमाणपत्र)',
    #          'Ward/Municipal Business Renewal (वडा व्यवसाय नवीकरण)'
    # AUDIT: 'Auditor Appointment & AGM Notice (लेखापरीक्षक नियुक्ति)',
    #        'Statutory Audit & Financial Statements (वैधानिक लेखापरीक्षण प्रतिवेदन)',
    #        'UDIN Generation & Tax Audit Sign-off (UDIN तथा लेखापरीक्षण प्रमाणीकरण)',
    #        'Annual General Meeting - AGM (वार्षिक साधारण सभा)'

    fiscal_year = Column(String(30), nullable=False, default="2082/83", index=True)  # e.g., 2082/83
    period_label = Column(String(80), nullable=True)  # e.g. 'Kartik 2083', 'Q1', 'Annual Poush Deadline'

    due_date_bs = Column(String(30), nullable=False, index=True)  # म्याद / अन्तिम मिति (वि.सं.)
    due_date_ad = Column(Date, nullable=True, index=True)
    completed_date_bs = Column(String(30), nullable=True)         # सम्पन्न मिति (वि.सं.)
    next_reminder_date_bs = Column(String(30), nullable=True, index=True)  # अर्को अनुस्मारक मिति (वि.सं.)

    status = Column(String(60), nullable=False, default="Pending (बाँकी)")
    # Pending (बाँकी), In Progress (प्रक्रियामा), Submitted (पेश गरिएको), Completed / Cleared (सम्पन्न / चुक्ता), Overdue (म्याद नाघेको)

    priority = Column(String(40), nullable=False, default="High")  # High, Medium, Low, Critical

    # Official Reference Numbers (OCR Chalani / IRD Submission No. / Tax Clearance No. / UDIN)
    reference_or_certificate_no = Column(String(120), nullable=True)
    auditor_or_officer_name = Column(String(150), nullable=True)
    udin_number = Column(String(80), nullable=True)

    # Government Fee / Fine / Service Charge
    gov_fee_or_penalty = Column(Float, default=0.0)
    professional_fee = Column(Float, default=0.0)

    assigned_to_id = Column(Integer, ForeignKey("staff_members.id", ondelete="SET NULL"), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("CorporateEntity", back_populates="activities")
    assigned_to = relationship("StaffMember", foreign_keys=[assigned_to_id])
