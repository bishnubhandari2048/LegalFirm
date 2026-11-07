import logging
from sqlalchemy.orm import Session
from app.models import (
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
from app.auth import hash_password
from app.bs_calendar import bs_to_ad, today_bs

logger = logging.getLogger("vidhicms.seed")


def seed_modules_and_company_data(db: Session):
    """Ensure Plug-and-Play Modules and Company (OCR + IRD Tax + Audit) sample records exist."""
    if db.query(SystemModuleConfig).count() == 0:
        mod_legal = SystemModuleConfig(
            module_key="legal",
            name_en="Legal & Court Litigation Module",
            name_np="मुद्दा तथा कानूनी व्यवस्थापन मोड्युल",
            description_en="Court cases (Mudda), Daily Hearings (Peshi/Tarekh), Legal Documents, Conflict Check & Fee Receipts.",
            description_np="अदालती मुद्दा, दैनिक पेशी/तारेख, कानूनी कागजात, विपक्षी द्वन्द्व जाँच र वकालत शुल्क रसिद व्यवस्थापन।",
            is_enabled=True,
            enable_ocr=True,
            enable_ird_tax=True,
            enable_audit=True,
            plan_tier="Enterprise",
        )
        mod_company = SystemModuleConfig(
            module_key="company_management",
            name_en="Company Management (OCR, IRD Tax & Audit) Module",
            name_np="कम्पनी व्यवस्थापन (OCR, आन्तरिक राजस्व कर र लेखापरीक्षण) मोड्युल",
            description_en="Plug-and-play module for Office of the Company Registrar (OCR) filings, IRD Tax returns & Tax Clearance, Statutory Audit (UDIN/AGM) & Periodic Compliance Reminders.",
            description_np="कम्पनी रजिष्ट्रारको कार्यालय (OCR) दर्ता/अद्यावधिक, आन्तरिक राजस्व (IRD) भ्याट/आयकर/कर चुक्ता, लेखापरीक्षण (Audit/UDIN) र म्याद अनुस्मारक प्रणाली।",
            is_enabled=True,
            enable_ocr=True,
            enable_ird_tax=True,
            enable_audit=True,
            plan_tier="Enterprise",
        )
        db.add_all([mod_legal, mod_company])
        db.flush()

    if db.query(CorporateEntity).count() == 0:
        first_staff = db.query(StaffMember).first()
        officer_id = first_staff.id if first_staff else None

        comp1 = CorporateEntity(
            company_name_en="Everest Trade & Logistics Pvt. Ltd.",
            company_name_np="एभरेष्ट ट्रेड एण्ड लजिस्टिक्स प्रा.लि.",
            company_type="Private Limited (प्रा.लि.)",
            ocr_registration_no="284512/078/079",
            registration_date_bs="2078-05-14",
            registration_date_ad=bs_to_ad("2078-05-14"),
            camis_username="everest_trade78",
            pan_vat_no="609845123",
            tax_registration_type="VAT (मु.अ.कर)",
            ird_office="आन्तरिक राजस्व कार्यालय, बानेश्वर (IRD Baneshwor)",
            tax_clearance_upto_fy="2081/82",
            authorized_capital=20000000.0,
            issued_capital=15000000.0,
            paidup_capital=15000000.0,
            shareholders_count=3,
            directors_summary="राजेश कुमार अग्रवाल (अध्यक्ष), सुमन श्रेष्ठ (प्रबन्ध सञ्चालक), अनिल शर्मा (सञ्चालक)",
            registered_address="काठमाडौँ म.न.पा.-१०, नयाँ बानेश्वर",
            contact_person="राजेश कुमार अग्रवाल",
            contact_phone="9802033445",
            contact_email="compliance@everesttrade.com.np",
            current_auditor_name="CA प्रकाश खतिवडा (Khatiwada & Associates)",
            auditor_ican_no="ICAN-COP-1142",
            last_agm_date_bs="2082-09-22",
            last_ocr_filed_fy="2081/82",
            annual_retainer_fee=180000.0,
            paid_retainer_amount=120000.0,
            due_retainer_amount=60000.0,
            assigned_officer_id=officer_id,
            status="Active (सक्रिय)",
            notes="मासिक भ्याट/ई-टीडीएस, वार्षिक लेखापरीक्षण र कम्पनी अद्यावधिक रिटेनर क्लाइन्ट।",
        )

        comp2 = CorporateEntity(
            company_name_en="Himalayan Hydro Engineering Ltd.",
            company_name_np="हिमालयन हाइड्रो इन्जिनियरिङ लि.",
            company_type="Public Limited (लि.)",
            ocr_registration_no="190421/075/076",
            registration_date_bs="2075-11-08",
            registration_date_ad=bs_to_ad("2075-11-08"),
            camis_username="himalayan_hydro",
            pan_vat_no="605112233",
            tax_registration_type="VAT (मु.अ.कर)",
            ird_office="मध्यमस्तरीय करदाता कार्यालय, बबरमहल (MTO Babarmahal)",
            tax_clearance_upto_fy="2081/82",
            authorized_capital=500000000.0,
            issued_capital=350000000.0,
            paidup_capital=350000000.0,
            shareholders_count=45,
            directors_summary="ई. देवेन्द्र थापा (अध्यक्ष), कविता गुरुङ, हरिभक्त पौडेल समेत ७ जना सञ्चालक",
            registered_address="ललितपुर म.न.पा.-३, झम्सिखेल",
            contact_person="ई. देवेन्द्र थापा",
            contact_phone="9851188990",
            contact_email="legal@himalayanhydro.com.np",
            current_auditor_name="CA बिनोद राज पन्त (B.R. Pant & Co.)",
            auditor_ican_no="ICAN-COP-0685",
            last_agm_date_bs="2082-09-28",
            last_ocr_filed_fy="2081/82",
            annual_retainer_fee=350000.0,
            paid_retainer_amount=350000.0,
            due_retainer_amount=0.0,
            assigned_officer_id=officer_id,
            status="Active (सक्रिय)",
            notes="पब्लिक लिमिटेड कम्पनी — दफा ७८, दफा ५१, विशेष साधारण सभा र कर चुक्ता व्यवस्थापन।",
        )

        comp3 = CorporateEntity(
            company_name_en="Kathmandu Tech Solutions Pvt. Ltd.",
            company_name_np="काठमाडौँ टेक सोलुसन्स प्रा.लि.",
            company_type="Private Limited (प्रा.लि.)",
            ocr_registration_no="319088/082/083",
            registration_date_bs="2082-04-19",
            registration_date_ad=bs_to_ad("2082-04-19"),
            camis_username="ktmtech_2082",
            pan_vat_no="610998877",
            tax_registration_type="VAT (मु.अ.कर)",
            ird_office="आन्तरिक राजस्व कार्यालय, पुतलीसडक (IRD Putalisadak)",
            tax_clearance_upto_fy="2081/82",
            authorized_capital=10000000.0,
            issued_capital=5000000.0,
            paidup_capital=5000000.0,
            shareholders_count=2,
            directors_summary="आयुष कँडेल (प्रबन्ध सञ्चालक), निशा भण्डारी (सञ्चालक)",
            registered_address="काठमाडौँ म.न.पा.-२८, पुतलीसडक",
            contact_person="आयुष कँडेल",
            contact_phone="9841908070",
            contact_email="aayush@ktmtech.io",
            current_auditor_name="CA प्रकाश खतिवडा (Khatiwada & Associates)",
            auditor_ican_no="ICAN-COP-1142",
            last_agm_date_bs="2082-09-15",
            last_ocr_filed_fy="2081/82",
            annual_retainer_fee=120000.0,
            paid_retainer_amount=60000.0,
            due_retainer_amount=60000.0,
            assigned_officer_id=officer_id,
            status="Active (सक्रिय)",
            notes="नयाँ IT कम्पनी — ३ महले उद्देश्य संशोधन, शेयर लगत र मासिक भ्याट/ई-टीडीएस कार्य।",
        )

        db.add_all([comp1, comp2, comp3])
        db.flush()

        activities = [
            # OCR Activities
            ComplianceActivity(
                company_id=comp1.id,
                category="OCR",
                activity_type="Section 78 Annual Return & AGM Minutes Filing (दफा ७८ वार्षिक विवरण र साधारण सभा)",
                fiscal_year="2082/83",
                period_label="Poush End Deadline (पुस मसान्त)",
                due_date_bs="2083-09-29",
                due_date_ad=bs_to_ad("2083-09-29"),
                next_reminder_date_bs="2083-09-10",
                status="In Progress (प्रक्रियामा)",
                priority="Critical",
                reference_or_certificate_no="CAMIS-88219",
                assigned_to_id=officer_id,
                remarks="कम्पनी ऐन दफा ७८ बमोजिम पुस मसान्तभित्र लेखापरीक्षण प्रतिवेदन र साधारण सभा निर्णय अपलोड गर्ने।",
            ),
            ComplianceActivity(
                company_id=comp3.id,
                category="OCR",
                activity_type="Share Transfer & Section 51 Share Lagat Update (शेयर खरिद-बिक्री तथा दफा ५१ शेयर लगत)",
                fiscal_year="2082/83",
                period_label="Within 30 Days of Allotment",
                due_date_bs="2083-07-28",
                due_date_ad=bs_to_ad("2083-07-28"),
                next_reminder_date_bs="2083-07-22",
                status="Submitted (पेश गरिएको)",
                priority="High",
                reference_or_certificate_no="OCR-SL-44102",
                gov_fee_or_penalty=5000.0,
                professional_fee=15000.0,
                assigned_to_id=officer_id,
                remarks="CAMIS मा शेयर लगत दर्ताको लागि निवेदन पेश भएको, रजिष्ट्रार कार्यालयबाट स्वीकृतिको चरणमा।",
            ),
            ComplianceActivity(
                company_id=comp2.id,
                category="OCR",
                activity_type="Capital Increase & 3-Mahale MOA/AOA Amendment (पूँजी वृद्धि र ३ महले प्रबन्धपत्र संशोधन)",
                fiscal_year="2082/83",
                period_label="Special General Meeting (SGM)",
                due_date_bs="2083-08-15",
                due_date_ad=bs_to_ad("2083-08-15"),
                next_reminder_date_bs="2083-08-05",
                status="Pending (बाँकी)",
                priority="High",
                gov_fee_or_penalty=15000.0,
                professional_fee=35000.0,
                assigned_to_id=officer_id,
                remarks="विशेष साधारण सभाबाट अधिकृत पूँजी वृद्धि प्रस्ताव पारित गरी ३ महले विवरण OCR मा पेश गर्ने।",
            ),
            # IRD Tax Activities
            ComplianceActivity(
                company_id=comp1.id,
                category="IRD_TAX",
                activity_type="Monthly VAT Return & e-TDS Verification (मासिक मु.अ.कर तथा ई-टीडीएस दाखिला)",
                fiscal_year="2082/83",
                period_label="Kartik 25 Deadline (कार्तिक २५ गतेभित्र)",
                due_date_bs="2083-07-25",
                due_date_ad=bs_to_ad("2083-07-25"),
                next_reminder_date_bs="2083-07-20",
                status="Pending (बाँकी)",
                priority="Critical",
                assigned_to_id=officer_id,
                remarks="असोज महिनाको खरिद-बिक्री खाता रुजु गरी IRD पोर्टलमा भ्याट विवरण र e-TDS दाखिला गर्ने।",
            ),
            ComplianceActivity(
                company_id=comp1.id,
                category="IRD_TAX",
                activity_type="Annual Income Tax Return D-03 & Tax Clearance Certificate (वार्षिक आयकर D-03 र कर चुक्ता प्रमाणपत्र)",
                fiscal_year="2082/83",
                period_label="FY 2081/82 Clearance",
                due_date_bs="2083-06-30",
                due_date_ad=bs_to_ad("2083-06-30"),
                completed_date_bs="2083-06-25",
                next_reminder_date_bs="2083-06-25",
                status="Completed / Cleared (सम्पन्न / चुक्ता)",
                priority="Critical",
                reference_or_certificate_no="IRD-TCC-2082-99104",
                auditor_or_officer_name="आन्तरिक राजस्व कार्यालय, बानेश्वर",
                assigned_to_id=officer_id,
                remarks="आ.व. २०८१/८२ को D-03 विवरण दाखिला गरी कर चुक्ता प्रमाणपत्र (Tax Clearance Certificate) प्राप्त भइसकेको।",
            ),
            ComplianceActivity(
                company_id=comp2.id,
                category="IRD_TAX",
                activity_type="Estimated Income Tax Return & 1st Installment 40% (अनुमानित आयकर र प्रथम किस्ता ४०%)",
                fiscal_year="2082/83",
                period_label="Poush End (पुस मसान्त)",
                due_date_bs="2083-09-29",
                due_date_ad=bs_to_ad("2083-09-29"),
                next_reminder_date_bs="2083-09-15",
                status="Pending (बाँकी)",
                priority="High",
                assigned_to_id=officer_id,
                remarks="पुस मसान्तभित्र चालु आ.व. को अनुमानित आयकर विवरण र ४०% प्रथम किस्ता रकम जम्मा गर्नुपर्ने।",
            ),
            # AUDIT Activities
            ComplianceActivity(
                company_id=comp1.id,
                category="AUDIT",
                activity_type="Statutory Audit Report & ICAN UDIN Sign-off (वैधानिक लेखापरीक्षण प्रतिवेदन र UDIN जारी)",
                fiscal_year="2082/83",
                period_label="FY 2082/83 Statutory Audit",
                due_date_bs="2083-08-25",
                due_date_ad=bs_to_ad("2083-08-25"),
                next_reminder_date_bs="2083-08-10",
                status="In Progress (प्रक्रियामा)",
                priority="High",
                auditor_or_officer_name="CA प्रकाश खतिवडा (ICAN-COP-1142)",
                udin_number="261107CA01142A99",
                professional_fee=45000.0,
                assigned_to_id=officer_id,
                remarks="ट्रायल ब्यालेन्स र बैंक स्टेटमेन्ट रुजु सम्पन्न, अन्तिम लेखापरीक्षण प्रतिवेदन र UDIN जारी हुने चरणमा।",
            ),
            ComplianceActivity(
                company_id=comp2.id,
                category="AUDIT",
                activity_type="Auditor Appointment Notification under Sec 111 (लेखापरीक्षक नियुक्ति जानकारी)",
                fiscal_year="2082/83",
                period_label="AGM Resolution",
                due_date_bs="2083-07-30",
                due_date_ad=bs_to_ad("2083-07-30"),
                next_reminder_date_bs="2083-07-24",
                status="Pending (बाँकी)",
                priority="Medium",
                auditor_or_officer_name="CA बिनोद राज पन्त (ICAN-COP-0685)",
                assigned_to_id=officer_id,
                remarks="आगामी आ.व. का लागि लेखापरीक्षक नियुक्तिको सहमति पत्र र सञ्चालक समिति निर्णय OCR मा पेश गर्ने।",
            ),
        ]
        db.add_all(activities)
        db.commit()


def seed_initial_data(db: Session):
    """Populate realistic Nepal Law Firm + Corporate/OCR/Tax/Audit initial records."""
    if db.query(StaffMember).count() > 0:
        # Ensure new modular tables are also seeded on existing installations
        seed_modules_and_company_data(db)
        return

    logger.info("Seeding initial Law Firm & Corporate Compliance data (Nepali + English)...")
    cur_bs = today_bs()

    # 1. वकिल तथा कर्मचारी विवरण (Advocates, Auditors & Staff)
    adv_ramesh = StaffMember(
        full_name="वरिष्ठ अधिवक्ता रमेश प्रसाद शर्मा (Sr. Adv. Ramesh P. Sharma)",
        role="admin",
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
        notes="प्रमुख वरिष्ठ अधिवक्ता तथा कार्यालय प्रमुख",
    )
    adv_sunita = StaffMember(
        full_name="अधिवक्ता सुनिता अधिकारी (Adv. Sunita Adhikari)",
        role="advocate",
        designation="जिम्मेवार अधिवक्ता (Senior Associate Advocate)",
        bar_council_no="NBC-8921",
        specialization="अंशबण्डा, सम्बन्ध विच्छेद तथा पारिवारिक कानून (Family & Property Law)",
        phone="9841567890",
        email="sunita.adhikari@vidhilaw.com.np",
        address="पाटनढोका, ललितपुर",
        username="sunita",
        password_hash=hash_password("lawfirm123"),
        is_active=True,
    )
    adv_dipak = StaffMember(
        full_name="अधिवक्ता / CA दिपक राज भण्डारी (Adv. & Tax Advisor Dipak Bhandari)",
        role="advocate",
        designation="कर्पोरेट अधिवक्ता तथा कर/लेखापरीक्षण प्रमुख (Corporate, OCR & Tax Lead)",
        bar_council_no="NBC-11204 / ICAN-1142",
        specialization="OCR कम्पनी दर्ता, आन्तरिक राजस्व कर (IRD), लेखापरीक्षण र बैंकिङ कसूर",
        phone="9801234567",
        email="dipak.bhandari@vidhilaw.com.np",
        address="बबरमहल, काठमाडौँ",
        username="dipak",
        password_hash=hash_password("lawfirm123"),
        is_active=True,
    )
    staff_kamal = StaffMember(
        full_name="कमल थापा मगर (Kamal Thapa Magar)",
        role="staff",
        designation="सहायक कर्मचारी / अदालती फाँट र OCR/IRD सहयोगी (Legal & Corporate Clerk)",
        bar_council_no="",
        specialization="अदालत तारेख, कम्पनी रजिष्ट्रार (OCR) र कर कार्यालय (IRD) फायलिङ",
        phone="9849112233",
        email="kamal.thapa@vidhilaw.com.np",
        address="कोटेश्वर, काठमाडौँ",
        username="kamal",
        password_hash=hash_password("lawfirm123"),
        is_active=True,
    )
    staff_asmita = StaffMember(
        full_name="अस्मिता गुरुङ (Asmita Gurung)",
        role="staff",
        designation="सहायक कर्मचारी / लेखा तथा कागजात अभिलेख (Finance & Docs Assistant)",
        bar_council_no="",
        specialization="रसिद, आर्थिक लेखा, भ्याट/ई-टीडीएस अभिलेख र कागजात व्यवस्थापन",
        phone="9860998877",
        email="asmita.gurung@vidhilaw.com.np",
        address="नयाँ बानेश्वर, काठमाडौँ",
        username="asmita",
        password_hash=hash_password("lawfirm123"),
        is_active=True,
    )

    db.add_all([adv_ramesh, adv_sunita, adv_dipak, staff_kamal, staff_asmita])
    db.flush()

    # 2. क्लाइन्टको विवरण (Clients)
    c1 = Client(
        first_name="हरिबहादुर",
        last_name="श्रेष्ठ",
        full_name="हरिबहादुर श्रेष्ठ (Hari Bahadur Shrestha)",
        address="काठमाडौँ म.न.पा.-१०, नयाँ बानेश्वर",
        district="काठमाडौँ",
        phone="9851144556",
        alt_phone="9841223344",
        email="harishrestha@gmail.com",
        citizenship_no="२७-०१-७१-०४५२१",
        citizenship_district="काठमाडौँ",
        citizenship_issue_date_bs="2071-04-12",
        father_or_spouse_name="स्व. कृष्णबहादुर श्रेष्ठ",
        occupation="व्यापार / घरजग्गा",
        notes="पैतृक सम्पत्तिको अंशबण्डा र जग्गा खिचलो सम्बन्धी मुख्य क्लाइन्ट",
    )
    c2 = Client(
        first_name="सीता देवी",
        last_name="पौडेल",
        full_name="सीता देवी पौडेल (Sita Devi Paudel)",
        address="ललितपुर म.न.पा.-५, पुल्चोक, ललितपुर",
        district="ललितपुर",
        phone="9841778899",
        email="sitapaudel.np@gmail.com",
        citizenship_no="२५-०१-७४-०८९१२",
        citizenship_district="ललितपुर",
        citizenship_issue_date_bs="2074-09-05",
        father_or_spouse_name="रामचन्द्र पौडेल",
        occupation="शिक्षण सेवा",
        notes="सम्बन्ध विच्छेद र अंश मानाचामल मुद्दा",
    )
    c3 = Client(
        first_name="राजेश कुमार",
        last_name="अग्रवाल",
        full_name="राजेश कुमार अग्रवाल (Rajesh Kumar Agrawal)",
        address="काठमाडौँ म.न.पा.-१, नक्साल (स्थायी: विराटनगर-७, मोरङ)",
        district="काठमाडौँ",
        phone="9802033445",
        email="rajesh.agrawal@everesttrade.com.np",
        citizenship_no="०५-०१-६८-११२३४",
        citizenship_district="मोरङ",
        citizenship_issue_date_bs="2068-02-19",
        father_or_spouse_name="मदनलाल अग्रवाल",
        occupation="उद्योगी / व्यवसायी",
        notes="लेनदेन, चेक अनादर र एभरेष्ट ट्रेड एण्ड लजिस्टिक्स प्रा.लि. को सञ्चालक",
    )
    c4 = Client(
        first_name="कल्पना",
        last_name="तामाङ",
        full_name="कल्पना तामाङ (Kalpana Tamang)",
        address="सूर्यविनायक न.पा.-४, भक्तपुर",
        district="भक्तपुर",
        phone="9861334455",
        email="",
        citizenship_no="२६-०१-७६-०३३१९",
        citizenship_district="भक्तपुर",
        citizenship_issue_date_bs="2076-11-22",
        father_or_spouse_name="सोमबहादुर तामाङ",
        occupation="कृषि तथा साना व्यवसाय",
        notes="जग्गा जालसाजी र लिखत बदर मुद्दा",
    )

    db.add_all([c1, c2, c3, c4])
    db.flush()

    # 3. मुद्दाको विवरण (Legal Cases)
    case1 = LegalCase(
        case_number="०८२-CP-०४१२",
        filing_number="दर्ता नं. १२८९/०८२",
        case_title="हरिबहादुर श्रेष्ठ विरुद्ध श्यामबहादुर श्रेष्ठ समेत",
        court_name="काठमाडौँ जिल्ला अदालत (Kathmandu District Court)",
        bench_section="फाँट नं. ५ (देवानी)",
        case_type="अंशबण्डा (Partition of Property)",
        client_id=c1.id,
        client_party_role="वादी (Plaintiff)",
        opponent_name="श्यामबहादुर श्रेष्ठ र राममाया श्रेष्ठ",
        opponent_address="काठमाडौँ म.न.पा.-१०, बानेश्वर",
        opponent_contact="9841098765",
        opponent_counsel="अधिवक्ता विनोद कार्की",
        registration_date_bs="2082-08-14",
        registration_date_ad=bs_to_ad("2082-08-14"),
        status="तारेखमा / विचाराधीन (Active)",
        deal_amount=150000.0,
        paid_amount=90000.0,
        due_amount=60000.0,
        advocate_id=adv_ramesh.id,
        assistant_id=staff_kamal.id,
        waris_name="कमल थापा मगर",
        next_hearing_date_bs=cur_bs,
        next_hearing_date_ad=bs_to_ad(cur_bs),
        summary="सगोलको काठमाडौँ कि.नं. ४१२ र ४१५ को घरजग्गा र बैंक मौज्दात ३ भाग लगाई १ भाग अंश छुट्याई पाऊँ भन्ने फिराद दाबी।",
    )

    case2 = LegalCase(
        case_number="०८२-FM-०८८५",
        filing_number="दर्ता नं. २४१०/०८२",
        case_title="सीता देवी पौडेल विरुद्ध सुवास चन्द्र पौडेल",
        court_name="ललितपुर जिल्ला अदालत (Lalitpur District Court)",
        bench_section="पारिवारिक इजलास - फाँट नं. २",
        case_type="सम्बन्ध विच्छेद र अंश (Divorce & Alimony)",
        client_id=c2.id,
        client_party_role="वादी (Plaintiff)",
        opponent_name="सुवास चन्द्र पौडेल",
        opponent_address="ललितपुर म.न.पा.-५, पुल्चोक",
        opponent_contact="9851088776",
        opponent_counsel="अधिवक्ता प्रकाश न्यौपाने",
        registration_date_bs="2082-11-03",
        registration_date_ad=bs_to_ad("2082-11-03"),
        status="बहसको क्रममा (In Arguments)",
        deal_amount=85000.0,
        paid_amount=85000.0,
        due_amount=0.0,
        advocate_id=adv_sunita.id,
        assistant_id=staff_asmita.id,
        waris_name="सीता देवी पौडेल (स्वयं)",
        next_hearing_date_bs="2083-07-25",
        next_hearing_date_ad=bs_to_ad("2083-07-25"),
        summary="मुलुकी देवानी संहिता, २०७४ को दफा ९३ बमोजिम अंश सहित सम्बन्ध विच्छेद र नाबालकको संरक्षकत्व दिलाई पाऊँ।",
    )

    case3 = LegalCase(
        case_number="०८३-CB-०११९",
        filing_number="दर्ता नं. ०३४५/०८३",
        case_title="राजेश कुमार अग्रवाल विरुद्ध नविन ट्रेडिङ प्रा.लि. (सञ्चालक दिपेश शाह)",
        court_name="उच्च अदालत पाटन (High Court Patan)",
        bench_section="वाणिज्य इजलास - फाँट नं. ३",
        case_type="चेक अनादर / लेनदेन (Cheque Bounce & Recovery)",
        client_id=c3.id,
        client_party_role="वादी / जाहेरवाला (Plaintiff)",
        opponent_name="दिपेश कुमार शाह (नविन ट्रेडिङ प्रा.लि.)",
        opponent_address="काठमाडौँ म.न.पा.-२२, न्यूरोड",
        opponent_contact="9801992211",
        opponent_counsel="अधिवक्ता सरोज के.सी.",
        registration_date_bs="2083-02-18",
        registration_date_ad=bs_to_ad("2083-02-18"),
        status="विचाराधीन (Active)",
        deal_amount=200000.0,
        paid_amount=120000.0,
        due_amount=80000.0,
        advocate_id=adv_dipak.id,
        assistant_id=staff_kamal.id,
        waris_name="कमल थापा मगर",
        next_hearing_date_bs="2083-07-22",
        next_hearing_date_ad=bs_to_ad("2083-07-22"),
        summary="रु. ४५,००,०००/- को चेक पर्याप्त मौज्दात नभई ३ पटक बाउन्स भएकोले साँवा, ब्याज र जरिवाना भराइ पाऊँ।",
    )

    case4 = LegalCase(
        case_number="०८१-CR-१०९२",
        filing_number="दर्ता नं. ३९०१/०८१",
        case_title="कल्पना तामाङ विरुद्ध हरिहर थापा समेत",
        court_name="भक्तपुर जिल्ला अदालत (Bhaktapur District Court)",
        bench_section="फाँट नं. ४",
        case_type="दूषित लिखत बदर र जालसाजी (Deed Cancellation & Fraud)",
        client_id=c4.id,
        client_party_role="वादी (Plaintiff)",
        opponent_name="हरिहर थापा र मालपोत फाँट सहयोगी",
        opponent_address="सूर्यविनायक न.पा.-६, भक्तपुर",
        opponent_contact="9841665544",
        opponent_counsel="अधिवक्ता राजेन्द्र श्रेष्ठ",
        registration_date_bs="2081-09-20",
        registration_date_ad=bs_to_ad("2081-09-20"),
        status="फैसला भएको (Decided)",
        deal_amount=110000.0,
        paid_amount=95000.0,
        due_amount=15000.0,
        advocate_id=adv_ramesh.id,
        assistant_id=staff_asmita.id,
        waris_name="कल्पना तामाङ",
        next_hearing_date_bs="2083-08-05",
        next_hearing_date_ad=bs_to_ad("2083-08-05"),
        summary="झुक्याई पारित गराएको राजीनामा लिखत बदर गरी साविक बमोजिम जग्गा दर्ता कायम गरिपाऊँ।",
    )

    db.add_all([case1, case2, case3, case4])
    db.flush()

    # 4. पेशी विवरण (Hearings)
    hearings = [
        Hearing(
            case_id=case1.id,
            hearing_date_bs=cur_bs,
            hearing_date_ad=bs_to_ad(cur_bs),
            hearing_status="बहस / पेशी तोकिएको (Scheduled for Arguments)",
            bench_or_judge="इजलास नं. ५",
            next_hearing_date_bs="2083-08-12",
            next_hearing_date_ad=bs_to_ad("2083-08-12"),
            outcome="तायदाती फाँटवारी प्राप्त भएको, आज बकपत्र र अन्तरिम आदेश सम्बन्धी बहस हुने।",
            attended_by_id=adv_ramesh.id,
            remarks="आजको मुख्य पेशी",
        ),
        Hearing(
            case_id=case2.id,
            hearing_date_bs="2083-06-14",
            hearing_date_ad=bs_to_ad("2083-06-14"),
            hearing_status="तारेख / मेलमिलाप (Tarekh / Mediation)",
            bench_or_judge="इजलास नं. २ - माननीय न्यायाधीश श्री शारदा कोइराला",
            next_hearing_date_bs="2083-07-25",
            next_hearing_date_ad=bs_to_ad("2083-07-25"),
            outcome="मेलमिलाप केन्द्रमा सहमति नजुटेकोले अन्तिम बहसका लागि पेशी तोकिएको।",
            attended_by_id=adv_sunita.id,
        ),
    ]
    db.add_all(hearings)

    # 5. आर्थिक विवरण (Payments)
    payments = [
        PaymentRecord(
            case_id=case1.id,
            client_id=c1.id,
            amount=90000.0,
            payment_date_bs="2082-08-14",
            payment_date_ad=bs_to_ad("2082-08-14"),
            payment_method="बैंक ट्रान्सफर (Bank Transfer)",
            receipt_number="RCP-2082-0001",
            purpose="पेश्की तथा बहस शुल्क (Advance & Arguments Fee)",
            reference_no="NABIL-TXN-88412",
            received_by_id=staff_asmita.id,
        ),
        PaymentRecord(
            case_id=case2.id,
            client_id=c2.id,
            amount=85000.0,
            payment_date_bs="2082-11-03",
            payment_date_ad=bs_to_ad("2082-11-03"),
            payment_method="eSewa",
            receipt_number="RCP-2082-0002",
            purpose="पूरा वकालत शुल्क चुक्ता (Full Settlement)",
            reference_no="ESEWA-0991245",
            received_by_id=staff_asmita.id,
        ),
        PaymentRecord(
            case_id=case3.id,
            client_id=c3.id,
            amount=120000.0,
            payment_date_bs="2083-02-18",
            payment_date_ad=bs_to_ad("2083-02-18"),
            payment_method="चेक (Cheque)",
            receipt_number="RCP-2083-0003",
            purpose="पेश्की तथा बहस शुल्क (Legal Retainer & Filing)",
            reference_no="GIME-CHQ-449012",
            received_by_id=adv_dipak.id,
        ),
        PaymentRecord(
            case_id=case4.id,
            client_id=c4.id,
            amount=95000.0,
            payment_date_bs="2083-06-08",
            payment_date_ad=bs_to_ad("2083-06-08"),
            payment_method="नगद (Cash)",
            receipt_number="RCP-2083-0004",
            purpose="वकालत र फैसला बहस शुल्क",
            reference_no="CASH",
            received_by_id=staff_asmita.id,
        ),
    ]
    db.add_all(payments)

    # 6. कागजात सम्बन्धी विवरण (Documents)
    documents = [
        CaseDocument(
            case_id=case1.id,
            client_id=c1.id,
            document_name="जग्गाधनी दर्ता प्रमाणपुर्जा (लालपुर्जा - कि.नं. ४१२ र ४१५)",
            document_type="मूल कागजात (Original)",
            status="कार्यालयमा सुरक्षित (In Office)",
            received_date_bs="2082-08-10",
            received_date_ad=bs_to_ad("2082-08-10"),
            handover_person="हरिबहादुर श्रेष्ठ",
            remarks="अदालतमा भिडाउनको लागि मूल लालपुर्जा सेफमा राखिएको",
        ),
        CaseDocument(
            case_id=case3.id,
            client_id=c3.id,
            document_name="बाउन्स भएको सक्कल चेक (रु. ४५,००,०००) र ३ वटा चेक बाउन्स स्लिप",
            document_type="मूल कागजात (Original)",
            status="कार्यालयमा सुरक्षित (In Office)",
            received_date_bs="2083-02-15",
            received_date_ad=bs_to_ad("2083-02-15"),
            handover_person="राजेश कुमार अग्रवाल",
            remarks="बैंकिङ कसूर र चेक अनादर प्रमाणको लागि सक्कल कागजात",
        ),
    ]
    db.add_all(documents)
    db.commit()

    # 7. Seed Plug-and-Play Modules & Company Management (OCR + IRD Tax + Audit)
    seed_modules_and_company_data(db)
    logger.info("Initial Law Firm & Corporate Compliance data seeded successfully.")
