# ⚖️ विधि ल फर्म व्यवस्थापन प्रणाली (Vidhi Law Firm Management System)

A full-stack **FastAPI + MySQL** Law Firm Management System designed for Nepal legal practice with **Bilingual (Nepali + English)** interface and **Bikram Sambat (वि.सं. BS) ↔ Gregorian (ई.सं. AD)** date support.

---

## ✨ मुख्य विशेषताहरू (Core Features)

1. **क्लाइन्टको विवरण (Client Records)**
   - नाम, थर (`first_name`, `last_name`, `full_name`)
   - ठेगाना र जिल्ला (`address`, `district`)
   - सम्पर्क नम्बर र वैकल्पिक नम्बर (`phone`, `alt_phone`)
   - इमेल (`email` - optional)
   - नागरिकता नम्बर, जारी जिल्ला र मिति (`citizenship_no`, `citizenship_district`, `citizenship_issue_date_bs`)
   - तीनपुस्ते विवरणको लागि बाबु/पति/पत्नीको नाम (`father_or_spouse_name`)

2. **मुद्दाको विवरण (Case Management)**
   - मुद्दा नम्बर र दर्ता/दायर नम्बर (`case_number`, `filing_number`)
   - अदालतको नाम र फाँट/इजलास (`court_name`, `bench_section`)
   - मुद्दाको प्रकार (`case_type`: अंशबण्डा, लेनदेन, सम्बन्ध विच्छेद, चेक अनादर, लिखत बदर, जग्गा खिचलो, रिट निवेदन, फौजदारी आदि)
   - पक्षको हैसियत (वादी, प्रतिवादी, निवेदक, पुनरावेदक)
   - विपक्षीको नाम, ठेगाना र विपक्षीको वकिल (`opponent_name`, `opponent_address`, `opponent_counsel`)
   - मुद्दा दर्ता मिति (वि.सं. र ई.सं.)
   - पूर्ण मुद्दा फाइल प्रिन्ट (`/print/case/{id}`)

3. **पेशी विवरण (Hearings / Peshi & Tarekh Tracking)**
   - पेशी मिति (वि.सं. र ई.सं.)
   - पेशीको अवस्था (`hearing_status`: तारेख, साधारण तारेख, बहस, आदेश, फैसला, स्थगित, हेर्न नभ्याइने, हेर्दाहेर्दै आदि)
   - अर्को पेशी मिति (`next_hearing_date_bs` - स्वतः मुद्दा फाइल र दैनिक पेशी सूचीमा अद्यावधिक हुने)
   - पेशीको नतिजा / आदेशको संक्षिप्त व्यहोरा (`outcome`)

4. **आर्थिक विवरण र रसिद (Financials, Billing & Printable Receipts)**
   - सहमति भएको शुल्क (`deal_amount` / Deal Amount)
   - प्राप्त रकम (`paid_amount` / Paid Amount)
   - बाँकी रकम (`due_amount` / Due Amount — स्वतः गणना हुने)
   - भुक्तानी मिति (`payment_date_bs`)
   - भुक्तानीको माध्यम (`payment_method`: नगद, बैंक ट्रान्सफर, चेक, eSewa, Khalti, ConnectIPS)
   - रसिद नम्बर (`receipt_number`) र **आधिकारिक रसिद प्रिन्ट** (`/print/receipt/{id}`)

5. **कागजात सम्बन्धी विवरण (Document Inventory & Digital File Upload)**
   - प्राप्त भएका कागजातहरूको सूची (`document_name`: लालपुर्जा, नागरिकता, तमसुक, वकालतनामा आदि)
   - मूल कागजात वा प्रतिलिपि (`document_type`: मूल कागजात / प्रतिलिपि / प्रमाणित प्रतिलिपि)
   - कागजात बुझाएको र फिर्ता गरेको मिति (`received_date_bs`, `returned_date_bs`)
   - डिजिटल स्क्यान फाइल अपलोड र डाउनलोड (`PDF / Image`)

6. **वकिल तथा कर्मचारी विवरण र लगइन (Advocates, Staff & RBAC Auth)**
   - जिम्मेवार अधिवक्ताको नाम, नेपाल बार काउन्सिल नं. र विशेषज्ञता
   - सहायक कर्मचारीको नाम र जिम्मेवारी
   - सम्पर्क विवरण र Role-Based JWT/Cookie Authentication (`admin`, `advocate`, `staff`)

7. **थप कानूनी उपकरणहरू (Additional Legal Utilities)**
   - **दैनिक तथा आगामी पेशी सूची (Daily Cause List Dashboard)**
   - **विपक्षी द्वन्द्व जाँच (Conflict of Interest Search)**
   - **विक्रम संवत् (BS) ↔ ई.सं. (AD) मिति रूपान्तरण (Date Converter)**

---

## 🚀 सञ्चालन गर्ने तरिका (How to Run)

1. **MySQL Configuration (`.env`)**:
   Configured to connect to your running Docker MySQL container (`127.0.0.1:3306`, user `root`, password `password`, database `lawfirm_db`). The database `lawfirm_db` (`utf8mb4`) and tables are created automatically on startup.

2. **Start the Server**:
   ```powershell
   python run.py
   ```
   Or using Uvicorn directly:
   ```powershell
   uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
   ```

3. **Open in Browser**:
   - **Main Application UI**: http://127.0.0.1:8080
   - **Swagger API Docs**: http://127.0.0.1:8080/docs

### 🔑 Default Demo Login Credentials
| Role | Username | Password |
| :--- | :--- | :--- |
| **वरिष्ठ अधिवक्ता / Admin** | `admin` | `admin123` |
| **जिम्मेवार अधिवक्ता (Advocate)** | `sunita` | `lawfirm123` |
| **जिम्मेवार अधिवक्ता (Advocate)** | `dipak` | `lawfirm123` |
| **सहायक कर्मचारी (Staff)** | `kamal` | `lawfirm123` |
