from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# 0A. Enterprise Multi-Tenant SaaS & Tenant-Scoped LOV Schemas
# ============================================================

class TenantCreate(BaseModel):
    tenant_code: str = Field(..., description="Unique tenant code e.g. FIRM-002")
    firm_name_en: str = Field(..., description="Law / Audit Firm Name in English")
    firm_name_np: Optional[str] = Field(default=None, description="Law / Audit Firm Name in Nepali")
    firm_subtitle: Optional[str] = "Advocates, Corporate Consultants & Tax Advisors"
    pan_vat_no: Optional[str] = None
    address: Optional[str] = "Kathmandu, Nepal"
    phone: str
    email: Optional[str] = None
    receipt_prefix: str = "RCP"
    subscription_plan: str = "Enterprise"
    subscription_status: str = "Active"
    subscription_expiry_bs: Optional[str] = "2084-12-30"
    max_users: int = 25
    enable_legal_module: bool = True
    enable_company_module: bool = True
    enable_ocr_sub: bool = True
    enable_ird_sub: bool = True
    enable_audit_sub: bool = True

    # Initial Tenant Admin Account Credentials (auto-provisioned)
    admin_full_name: str
    admin_username: str
    admin_password: str = "lawfirm123"
    admin_phone: Optional[str] = None


class TenantUpdate(BaseModel):
    firm_name_en: Optional[str] = None
    firm_name_np: Optional[str] = None
    firm_subtitle: Optional[str] = None
    pan_vat_no: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    receipt_prefix: Optional[str] = None
    subscription_plan: Optional[str] = None
    subscription_status: Optional[str] = None
    subscription_expiry_bs: Optional[str] = None
    max_users: Optional[int] = None
    enable_legal_module: Optional[bool] = None
    enable_company_module: Optional[bool] = None
    enable_ocr_sub: Optional[bool] = None
    enable_ird_sub: Optional[bool] = None
    enable_audit_sub: Optional[bool] = None
    is_active: Optional[bool] = None


class TenantLOVCreate(BaseModel):
    category: Optional[str] = Field(default=None, description="COURT_NAME | CASE_TYPE | HEARING_STATUS | CASE_STATUS | PARTY_ROLE | PAYMENT_METHOD | DOCUMENT_TYPE | IRD_OFFICE | COMPANY_TYPE")
    lov_group: Optional[str] = None
    value_en: Optional[str] = None
    value_np: Optional[str] = None
    label_en: Optional[str] = None
    label_np: Optional[str] = None
    sort_order: int = 10
    is_active: bool = True


class TenantLOVUpdate(BaseModel):
    value_en: Optional[str] = None
    value_np: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============================================================
# 0B. Plug-and-Play Module Subscription Schemas
# ============================================================

class ModuleConfigUpdate(BaseModel):
    is_enabled: bool
    enable_ocr: Optional[bool] = True
    enable_ird_tax: Optional[bool] = True
    enable_audit: Optional[bool] = True
    plan_tier: Optional[str] = "Enterprise"


# ============================================================
# 1. वकिल तथा कर्मचारी विवरण (Staff & Advocates) + Auth
# ============================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class StaffMemberBase(BaseModel):
    full_name: str = Field(..., min_length=1, description="पूरा नाम, थर")
    role: str = Field(default="advocate", description="admin | advocate | auditor | staff")
    designation: str = Field(default="अधिवक्ता (Advocate)")
    bar_council_no: Optional[str] = None
    specialization: Optional[str] = None
    phone: str
    alt_phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    username: str
    is_active: bool = True
    notes: Optional[str] = None


class StaffMemberCreate(StaffMemberBase):
    password: str = Field(default="lawfirm123", min_length=4)


class StaffMemberUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    designation: Optional[str] = None
    bar_council_no: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None
    alt_phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class StaffMemberOut(StaffMemberBase):
    id: int
    tenant_id: int
    created_at: Optional[datetime] = None
    active_cases_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 2. क्लाइन्टको विवरण (Client Schemas)
# ============================================================

class ClientBase(BaseModel):
    first_name: str
    last_name: str
    address: str
    district: Optional[str] = None
    phone: str
    alt_phone: Optional[str] = None
    email: Optional[str] = None
    citizenship_no: str
    citizenship_district: Optional[str] = None
    citizenship_issue_date_bs: Optional[str] = None
    father_or_spouse_name: Optional[str] = None
    occupation: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    phone: Optional[str] = None
    alt_phone: Optional[str] = None
    email: Optional[str] = None
    citizenship_no: Optional[str] = None
    citizenship_district: Optional[str] = None
    citizenship_issue_date_bs: Optional[str] = None
    father_or_spouse_name: Optional[str] = None
    occupation: Optional[str] = None
    notes: Optional[str] = None


# ============================================================
# 3. मुद्दाको विवरण (Legal Case Schemas)
# ============================================================

class LegalCaseBase(BaseModel):
    case_number: str
    filing_number: Optional[str] = None
    case_title: Optional[str] = None
    court_name: str
    bench_section: Optional[str] = None
    case_type: str
    client_id: int
    client_party_role: str = "वादी (Plaintiff)"
    opponent_name: str
    opponent_address: Optional[str] = None
    opponent_contact: Optional[str] = None
    opponent_counsel: Optional[str] = None
    registration_date_bs: str
    registration_date_ad: Optional[date] = None
    status: str = "विचाराधीन (Active)"
    deal_amount: float = 0.0
    advocate_id: Optional[int] = None
    assistant_id: Optional[int] = None
    waris_name: Optional[str] = None
    next_hearing_date_bs: Optional[str] = None
    next_hearing_date_ad: Optional[date] = None
    summary: Optional[str] = None


class LegalCaseCreate(LegalCaseBase):
    initial_paid_amount: Optional[float] = 0.0
    initial_payment_method: Optional[str] = "नगद (Cash)"
    initial_receipt_number: Optional[str] = None


class LegalCaseUpdate(BaseModel):
    case_number: Optional[str] = None
    filing_number: Optional[str] = None
    case_title: Optional[str] = None
    court_name: Optional[str] = None
    bench_section: Optional[str] = None
    case_type: Optional[str] = None
    client_id: Optional[int] = None
    client_party_role: Optional[str] = None
    opponent_name: Optional[str] = None
    opponent_address: Optional[str] = None
    opponent_contact: Optional[str] = None
    opponent_counsel: Optional[str] = None
    registration_date_bs: Optional[str] = None
    registration_date_ad: Optional[date] = None
    status: Optional[str] = None
    deal_amount: Optional[float] = None
    advocate_id: Optional[int] = None
    assistant_id: Optional[int] = None
    waris_name: Optional[str] = None
    next_hearing_date_bs: Optional[str] = None
    next_hearing_date_ad: Optional[date] = None
    summary: Optional[str] = None


# ============================================================
# 4. पेशी विवरण (Hearing / Peshi Schemas)
# ============================================================

class HearingBase(BaseModel):
    case_id: int
    hearing_date_bs: str
    hearing_date_ad: Optional[date] = None
    hearing_status: str
    bench_or_judge: Optional[str] = None
    next_hearing_date_bs: Optional[str] = None
    next_hearing_date_ad: Optional[date] = None
    outcome: Optional[str] = None
    attended_by_id: Optional[int] = None
    remarks: Optional[str] = None


class HearingCreate(HearingBase):
    update_case_status: Optional[str] = None


class HearingUpdate(BaseModel):
    hearing_date_bs: Optional[str] = None
    hearing_date_ad: Optional[date] = None
    hearing_status: Optional[str] = None
    bench_or_judge: Optional[str] = None
    next_hearing_date_bs: Optional[str] = None
    next_hearing_date_ad: Optional[date] = None
    outcome: Optional[str] = None
    attended_by_id: Optional[int] = None
    remarks: Optional[str] = None


# ============================================================
# 5. आर्थिक विवरण (Financial & Payment Schemas)
# ============================================================

class PaymentBase(BaseModel):
    case_id: int
    client_id: Optional[int] = None
    amount: float = Field(..., gt=0)
    payment_date_bs: str
    payment_date_ad: Optional[date] = None
    payment_method: str = Field(default="नगद (Cash)")
    receipt_number: Optional[str] = Field(default=None)
    purpose: str = "वकालत शुल्क (Legal Fee)"
    reference_no: Optional[str] = None
    remarks: Optional[str] = None
    received_by_id: Optional[int] = None


class PaymentCreate(PaymentBase):
    pass


class DealAmountUpdate(BaseModel):
    deal_amount: float = Field(..., ge=0)


# ============================================================
# 6. कागजात सम्बन्धी विवरण (Document Schemas)
# ============================================================

class CaseDocumentBase(BaseModel):
    case_id: int
    client_id: Optional[int] = None
    document_name: str
    document_type: str = Field(default="प्रतिलिपि (Copy)")
    status: str = Field(default="कार्यालयमा सुरक्षित (In Office)")
    received_date_bs: str
    received_date_ad: Optional[date] = None
    returned_date_bs: Optional[str] = None
    returned_date_ad: Optional[date] = None
    handover_person: Optional[str] = None
    remarks: Optional[str] = None


class CaseDocumentCreate(CaseDocumentBase):
    pass


class CaseDocumentUpdate(BaseModel):
    document_name: Optional[str] = None
    document_type: Optional[str] = None
    status: Optional[str] = None
    received_date_bs: Optional[str] = None
    returned_date_bs: Optional[str] = None
    handover_person: Optional[str] = None
    remarks: Optional[str] = None


# ============================================================
# 7. COMPANY MANAGEMENT MODULE (OCR, IRD TAX & AUDIT SCHEMAS)
# ============================================================

class CorporateEntityBase(BaseModel):
    company_name_en: str
    company_name_np: Optional[str] = None
    company_type: str = "Private Limited (प्रा.लि.)"
    ocr_registration_no: str
    registration_date_bs: str
    camis_username: Optional[str] = None
    pan_vat_no: str
    tax_registration_type: str = "VAT (मु.अ.कर)"
    ird_office: str = "आन्तरिक राजस्व कार्यालय, बानेश्वर"
    tax_clearance_upto_fy: Optional[str] = "2081/82"
    authorized_capital: float = 0.0
    issued_capital: float = 0.0
    paidup_capital: float = 0.0
    shareholders_count: int = 1
    directors_summary: Optional[str] = None
    registered_address: str
    contact_person: str
    contact_phone: str
    contact_email: Optional[str] = None
    current_auditor_name: Optional[str] = None
    auditor_ican_no: Optional[str] = None
    last_agm_date_bs: Optional[str] = None
    last_ocr_filed_fy: Optional[str] = "2081/82"
    annual_retainer_fee: float = 0.0
    paid_retainer_amount: float = 0.0
    client_id: Optional[int] = None
    assigned_officer_id: Optional[int] = None
    status: str = "Active (सक्रिय)"
    notes: Optional[str] = None


class CorporateEntityCreate(CorporateEntityBase):
    auto_generate_periodic_tasks: bool = True


class CorporateEntityUpdate(BaseModel):
    company_name_en: Optional[str] = None
    company_name_np: Optional[str] = None
    company_type: Optional[str] = None
    ocr_registration_no: Optional[str] = None
    registration_date_bs: Optional[str] = None
    camis_username: Optional[str] = None
    pan_vat_no: Optional[str] = None
    tax_registration_type: Optional[str] = None
    ird_office: Optional[str] = None
    tax_clearance_upto_fy: Optional[str] = None
    authorized_capital: Optional[float] = None
    issued_capital: Optional[float] = None
    paidup_capital: Optional[float] = None
    shareholders_count: Optional[int] = None
    directors_summary: Optional[str] = None
    registered_address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    current_auditor_name: Optional[str] = None
    auditor_ican_no: Optional[str] = None
    last_agm_date_bs: Optional[str] = None
    last_ocr_filed_fy: Optional[str] = None
    annual_retainer_fee: Optional[float] = None
    paid_retainer_amount: Optional[float] = None
    client_id: Optional[int] = None
    assigned_officer_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ComplianceActivityBase(BaseModel):
    company_id: int
    category: str = "OCR"
    activity_type: str
    fiscal_year: str = "2082/83"
    period_label: Optional[str] = None
    due_date_bs: str
    completed_date_bs: Optional[str] = None
    next_reminder_date_bs: Optional[str] = None
    status: str = "Pending (बाँकी)"
    priority: str = "High"
    reference_or_certificate_no: Optional[str] = None
    auditor_or_officer_name: Optional[str] = None
    udin_number: Optional[str] = None
    gov_fee_or_penalty: float = 0.0
    professional_fee: float = 0.0
    assigned_to_id: Optional[int] = None
    remarks: Optional[str] = None


class ComplianceActivityCreate(ComplianceActivityBase):
    pass


class ComplianceActivityUpdate(BaseModel):
    category: Optional[str] = None
    activity_type: Optional[str] = None
    fiscal_year: Optional[str] = None
    period_label: Optional[str] = None
    due_date_bs: Optional[str] = None
    completed_date_bs: Optional[str] = None
    next_reminder_date_bs: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    reference_or_certificate_no: Optional[str] = None
    auditor_or_officer_name: Optional[str] = None
    udin_number: Optional[str] = None
    gov_fee_or_penalty: Optional[float] = None
    professional_fee: Optional[float] = None
    assigned_to_id: Optional[int] = None
    remarks: Optional[str] = None
