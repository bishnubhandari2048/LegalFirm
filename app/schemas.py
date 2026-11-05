from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# 1. वकिल तथा कर्मचारी विवरण (Staff & Advocates) + Auth
# ============================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class StaffMemberBase(BaseModel):
    full_name: str = Field(..., min_length=1, description="पूरा नाम, थर")
    role: str = Field(default="advocate", description="admin | advocate | staff")
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
    created_at: Optional[datetime] = None
    active_cases_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 2. क्लाइन्टको विवरण (Client Schemas)
# ============================================================

class ClientBase(BaseModel):
    first_name: str = Field(..., description="नाम")
    last_name: str = Field(..., description="थर")
    address: str = Field(..., description="ठेगाना")
    district: Optional[str] = None
    phone: str = Field(..., description="सम्पर्क नम्बर")
    alt_phone: Optional[str] = None
    email: Optional[str] = None
    citizenship_no: str = Field(..., description="नागरिकता नम्बर")
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


class ClientOut(ClientBase):
    id: int
    full_name: str
    created_at: Optional[datetime] = None
    case_count: int = 0
    total_deal: float = 0.0
    total_paid: float = 0.0
    total_due: float = 0.0

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 3. मुद्दाको विवरण (Legal Case Schemas)
# ============================================================

class LegalCaseBase(BaseModel):
    case_number: str = Field(..., description="मुद्दा नम्बर (Case No.)")
    filing_number: Optional[str] = None
    case_title: Optional[str] = None
    court_name: str = Field(..., description="अदालतको नाम")
    bench_section: Optional[str] = None
    case_type: str = Field(..., description="मुद्दाको प्रकार (अंशबण्डा, लेनदेन, सम्बन्ध विच्छेद आदि)")
    client_id: int
    client_party_role: str = "वादी (Plaintiff)"
    opponent_name: str = Field(..., description="विपक्षीको नाम")
    opponent_address: Optional[str] = None
    opponent_contact: Optional[str] = None
    opponent_counsel: Optional[str] = None
    registration_date_bs: str = Field(..., description="मुद्दा दर्ता मिति (वि.सं.)")
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
    hearing_date_bs: str = Field(..., description="पेशी मिति (वि.सं.)")
    hearing_date_ad: Optional[date] = None
    hearing_status: str = Field(..., description="पेशीको अवस्था (तारेख, बहस, फैसला, स्थगित आदि)")
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
    amount: float = Field(..., gt=0, description="प्राप्त रकम")
    payment_date_bs: str = Field(..., description="भुक्तानी मिति (वि.सं.)")
    payment_date_ad: Optional[date] = None
    payment_method: str = Field(default="नगद (Cash)", description="नगद, बैंक, चेक, eSewa आदि")
    receipt_number: Optional[str] = Field(default=None, description="रसिद नम्बर")
    purpose: str = "वकालत शुल्क (Legal Fee)"
    reference_no: Optional[str] = None
    remarks: Optional[str] = None
    received_by_id: Optional[int] = None


class PaymentCreate(PaymentBase):
    pass


class DealAmountUpdate(BaseModel):
    deal_amount: float = Field(..., ge=0, description="सहमति भएको शुल्क (Deal Amount)")


# ============================================================
# 6. कागजात सम्बन्धी विवरण (Document Schemas)
# ============================================================

class CaseDocumentBase(BaseModel):
    case_id: int
    client_id: Optional[int] = None
    document_name: str = Field(..., description="प्राप्त भएका कागजातको नाम")
    document_type: str = Field(default="प्रतिलिपि (Copy)", description="मूल कागजात वा प्रतिलिपि")
    status: str = Field(default="कार्यालयमा सुरक्षित (In Office)")
    received_date_bs: str = Field(..., description="कागजात बुझाएको मिति (वि.सं.)")
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
