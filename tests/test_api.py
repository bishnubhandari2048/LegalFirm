from fastapi.testclient import TestClient
from app.main import app


def test_full_law_firm_workflow():
    with TestClient(app) as client:
        # 1. Health & UI Home
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

        home = client.get("/")
        assert home.status_code == 200
        assert "विधि व्यवस्थापन प्रणाली" in home.text

        # 2. Login as Admin / Senior Advocate
        login_res = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert login_res.status_code == 200, login_res.text
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Dashboard Stats & Cause List
        stats_res = client.get("/api/dashboard/stats", headers=headers)
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["counts"]["total_clients"] >= 4
        assert stats["counts"]["total_cases"] >= 4

        # 4. क्लाइन्टको विवरण (Create & Verify Client)
        new_client_res = client.post(
            "/api/clients",
            headers=headers,
            json={
                "first_name": "गंगाप्रसाद",
                "last_name": "ओली",
                "address": "भद्रपुर न.पा.-५, झापा",
                "district": "झापा",
                "phone": "9842611223",
                "email": "ganga.oli@example.com",
                "citizenship_no": "०४-०१-७०-०५५६६",
                "citizenship_district": "झापा",
                "citizenship_issue_date_bs": "2070-06-15",
                "father_or_spouse_name": "भवानीप्रसाद ओली",
                "occupation": "कृषि",
            },
        )
        assert new_client_res.status_code == 200, new_client_res.text
        client_id = new_client_res.json()["id"]
        assert "गंगाप्रसाद ओली" in new_client_res.json()["full_name"]

        # 5. वकिल तथा कर्मचारी विवरण (List Staff)
        staff_res = client.get("/api/staff", headers=headers)
        assert staff_res.status_code == 200
        staff_list = staff_res.json()
        assert len(staff_list) >= 5
        advocate_id = staff_list[0]["id"]
        assistant_id = staff_list[3]["id"]

        # 6. मुद्दाको विवरण (Create New Legal Case with Initial Advance)
        case_res = client.post(
            "/api/cases",
            headers=headers,
            json={
                "case_number": "०८३-WO-९९०२",
                "filing_number": "दर्ता नं. ९९०२/०८३",
                "court_name": "सर्वोच्च अदालत (Supreme Court of Nepal)",
                "bench_section": "संवैधानिक इजलास",
                "case_type": "रिट निवेदन (Writ Petition)",
                "client_id": client_id,
                "client_party_role": "निवेदक (Petitioner)",
                "opponent_name": "भूमिसुधार तथा मालपोत कार्यालय, झापा समेत",
                "registration_date_bs": "2083-07-18",
                "deal_amount": 125000.0,
                "initial_paid_amount": 45000.0,
                "initial_payment_method": "बैंक ट्रान्सफर (Bank Transfer)",
                "advocate_id": advocate_id,
                "assistant_id": assistant_id,
                "next_hearing_date_bs": "2083-07-28",
                "summary": "उत्प्रेषणयुक्त परमादेश जारी गरिपाऊँ।",
            },
        )
        assert case_res.status_code == 200, case_res.text
        case_data = case_res.json()
        case_id = case_data["id"]
        assert case_data["deal_amount"] == 125000.0
        assert case_data["paid_amount"] == 45000.0
        assert case_data["due_amount"] == 80000.0

        # 7. पेशी विवरण (Add Hearing / Peshi Record)
        hearing_res = client.post(
            "/api/hearings",
            headers=headers,
            json={
                "case_id": case_id,
                "hearing_date_bs": "2083-07-28",
                "hearing_status": "आदेश (Court Order)",
                "bench_or_judge": "एकल इजलास नं. २",
                "next_hearing_date_bs": "2083-08-19",
                "outcome": "विपक्षीहरूको नाममा १५ दिनभित्र लिखित जवाफ पेश गर्न कारण देखाउ आदेश जारी।",
            },
        )
        assert hearing_res.status_code == 200, hearing_res.text
        assert hearing_res.json()["next_hearing_date_bs"] == "2083-08-19"

        # 8. आर्थिक विवरण (Record Second Payment via eSewa & Check Due Balance)
        pay_res = client.post(
            "/api/finance/payments",
            headers=headers,
            json={
                "case_id": case_id,
                "amount": 30000.0,
                "payment_date_bs": "2083-07-29",
                "payment_method": "eSewa",
                "receipt_number": "RCP-TEST-2083-100",
                "purpose": "अन्तरिम आदेश बहस शुल्क",
                "reference_no": "ESEWA-TXN-778899",
            },
        )
        assert pay_res.status_code == 200, pay_res.text
        pay_data = pay_res.json()
        assert pay_data["case_paid_amount"] == 75000.0
        assert pay_data["case_due_amount"] == 50000.0

        # 9. कागजात सम्बन्धी विवरण (Add Document & Update Return Date)
        doc_res = client.post(
            "/api/documents",
            headers=headers,
            json={
                "case_id": case_id,
                "document_name": "मालपोत कार्यालयको निर्णय पर्चा र जग्गाधनी पुर्जा",
                "document_type": "मूल कागजात (Original)",
                "status": "कार्यालयमा सुरक्षित (In Office)",
                "received_date_bs": "2083-07-17",
                "handover_person": "गंगाप्रसाद ओली",
            },
        )
        assert doc_res.status_code == 200, doc_res.text
        doc_id = doc_res.json()["id"]

        # Update document return date
        ret_res = client.put(
            f"/api/documents/{doc_id}",
            headers=headers,
            json={"returned_date_bs": "2083-08-01"},
        )
        assert ret_res.status_code == 200
        assert ret_res.json()["returned_date_bs"] == "2083-08-01"

        # 10. Printable Receipt & Case File Dossier Views
        rcp_print = client.get(f"/print/receipt/{pay_data['id']}")
        assert rcp_print.status_code == 200
        assert "RCP-TEST-2083-100" in rcp_print.text

        case_print = client.get(f"/print/case/{case_id}")
        assert case_print.status_code == 200
        assert "०८३-WO-९९०२" in case_print.text

        # 11. Conflict Check & Date Conversion
        conf_res = client.get("/api/dashboard/conflict-check?q=गंगाप्रसाद", headers=headers)
        assert conf_res.status_code == 200
        assert conf_res.json()["has_conflict"] is True

        conv_res = client.get("/api/dashboard/date-convert?bs=2083-07-18")
        assert conv_res.status_code == 200
        assert conv_res.json()["ad"] != ""

        # Cleanup temporary test client & cascading case
        del_case = client.delete(f"/api/cases/{case_id}", headers=headers)
        assert del_case.status_code == 200
        del_client = client.delete(f"/api/clients/{client_id}", headers=headers)
        assert del_client.status_code == 200
