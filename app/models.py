from datetime import datetime, date
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


class StaffMember(Base):
    """वकिल तथा कर्मचारी विवरण (Advocates, Paralegals, Clerks & Admin Users)."""

    __tablename__ = "staff_members"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False, index=True)
    role = Column(String(40), nullable=False, default="advocate")  # admin, advocate, staff
    designation = Column(String(100), nullable=False, default="अधिवक्ता (Advocate)")
    bar_council_no = Column(String(60), nullable=True)  # नेपाल बार काउन्सिल दर्ता नं.
    specialization = Column(String(150), nullable=True)  # देवानी, फौजदारी, कर्पोरेट, रिट आदि
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
    father_or_spouse_name = Column(String(150), nullable=True)       # बाबु/पति/पत्नीको नाम (तीनपुस्ते विवरणको लागि)
    occupation = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cases = relationship("LegalCase", back_populates="client", cascade="all, delete-orphan")
    payments = relationship("PaymentRecord", back_populates="client")
    documents = relationship("CaseDocument", back_populates="client")


class LegalCase(Base):
    """मुद्दाको विवरण (Case Details, Assigned Counsel & Financial Agreement Summary)."""

    __tablename__ = "legal_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(100), nullable=False, unique=True, index=True)  # मुद्दा नम्बर (Case No.)
    filing_number = Column(String(100), nullable=True)  # दर्ता / दायर नम्बर
    case_title = Column(String(255), nullable=True)     # मुद्दाको शीर्षक (वादी वि. प्रतिवादी)
    court_name = Column(String(200), nullable=False, index=True)  # अदालतको नाम
    bench_section = Column(String(100), nullable=True)  # फाँट वा इजलास
    case_type = Column(String(120), nullable=False, index=True)   # मुद्दाको प्रकार (अंशबण्डा, लेनदेन, सम्बन्ध विच्छेद आदि)

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    client_party_role = Column(String(60), nullable=False, default="वादी (Plaintiff)")  # वादी, प्रतिवादी, निवेदक, पुनरावेदक

    opponent_name = Column(String(200), nullable=False, index=True)  # विपक्षीको नाम
    opponent_address = Column(String(255), nullable=True)            # विपक्षीको ठेगाना
    opponent_contact = Column(String(100), nullable=True)            # विपक्षीको सम्पर्क
    opponent_counsel = Column(String(150), nullable=True)            # विपक्षीको वकिल

    registration_date_bs = Column(String(30), nullable=False)        # मुद्दा दर्ता मिति (वि.सं.)
    registration_date_ad = Column(Date, nullable=True)               # मुद्दा दर्ता मिति (ई.सं.)

    status = Column(String(80), nullable=False, default="विचाराधीन (Active)")  # विचाराधीन, तारेखमा, फैसला भएको, मुल्तबी, मिलापत्र, पुनरावेदन

    # आर्थिक विवरण सारांश (Financial Deal Summary)
    deal_amount = Column(Float, nullable=False, default=0.0)  # सहमति भएको शुल्क (Deal Amount)
    paid_amount = Column(Float, nullable=False, default=0.0)  # प्राप्त रकम (Paid Amount)
    due_amount = Column(Float, nullable=False, default=0.0)   # बाँकी रकम (Due Amount)

    # वकिल तथा कर्मचारी विवरण (Assigned Advocate & Assistant Staff)
    advocate_id = Column(Integer, ForeignKey("staff_members.id", ondelete="SET NULL"), nullable=True)
    assistant_id = Column(Integer, ForeignKey("staff_members.id", ondelete="SET NULL"), nullable=True)
    waris_name = Column(String(150), nullable=True)  # वारेशको नाम (भएमा)

    next_hearing_date_bs = Column(String(30), nullable=True, index=True)  # अर्को पेशी मिति (वि.सं.)
    next_hearing_date_ad = Column(Date, nullable=True, index=True)        # अर्को पेशी मिति (ई.सं.)

    summary = Column(Text, nullable=True)  # मुद्दाको संक्षिप्त विवरण / मागदाबी
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

    hearing_date_bs = Column(String(30), nullable=False, index=True)  # पेशी मिति (वि.सं.)
    hearing_date_ad = Column(Date, nullable=True, index=True)         # पेशी मिति (ई.सं.)
    hearing_status = Column(String(100), nullable=False)              # पेशीको अवस्था (तारेख, बहस, फैसला, स्थगित, आदेश आदि)
    bench_or_judge = Column(String(150), nullable=True)               # इजलास नं. / न्यायाधीशको नाम
    next_hearing_date_bs = Column(String(30), nullable=True)          # अर्को पेशी मिति (वि.सं.)
    next_hearing_date_ad = Column(Date, nullable=True)                # अर्को पेशी मिति (ई.सं.)
    outcome = Column(Text, nullable=True)                             # पेशीको नतिजा / आदेशको व्यहोरा
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

    amount = Column(Float, nullable=False)                           # प्राप्त रकम (Paid Amount in transaction)
    payment_date_bs = Column(String(30), nullable=False, index=True) # भुक्तानी मिति (वि.सं.)
    payment_date_ad = Column(Date, nullable=True)                    # भुक्तानी मिति (ई.सं.)
    payment_method = Column(String(80), nullable=False, default="नगद (Cash)")  # नगद, बैंक, चेक, eSewa, Khalti, ConnectIPS
    receipt_number = Column(String(80), nullable=False, unique=True, index=True)  # रसिद नम्बर
    purpose = Column(String(120), nullable=False, default="वकालत शुल्क (Legal Fee)")  # पेश्की, वकालत शुल्क, अदालती दस्तुर
    reference_no = Column(String(120), nullable=True)                # चेक नं. वा ट्रान्जेक्सन आईडी
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

    document_name = Column(String(200), nullable=False, index=True)  # प्राप्त भएका कागजातको नाम
    document_type = Column(String(80), nullable=False, default="प्रतिलिपि (Copy)")  # मूल कागजात (Original) वा प्रतिलिपि (Copy)
    status = Column(String(80), nullable=False, default="कार्यालयमा सुरक्षित (In Office)")  # कार्यालयमा सुरक्षित, अदालतमा पेश, क्लाइन्टलाई फिर्ता
    received_date_bs = Column(String(30), nullable=False)            # कागजात बुझाएको/प्राप्त मिति (वि.सं.)
    received_date_ad = Column(Date, nullable=True)
    returned_date_bs = Column(String(30), nullable=True)             # कागजात फिर्ता गरेको मिति (वि.सं.)
    returned_date_ad = Column(Date, nullable=True)
    handover_person = Column(String(150), nullable=True)             # बुझाउने वा फिर्ता बुझिलिने व्यक्तिको नाम
    file_path = Column(String(500), nullable=True)                   # अपलोड गरिएको डिजिटल फाइल पाथ
    file_name = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    legal_case = relationship("LegalCase", back_populates="documents")
    client = relationship("Client", back_populates="documents")
