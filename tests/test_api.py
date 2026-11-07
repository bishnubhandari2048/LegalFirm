from fastapi.testclient import TestClient
from app.main import app


def test_full_law_firm_and_company_compliance_workflow():
    with TestClient(app) as client:
        # 1. Health & UI Home
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

        home = client.get("/")
        assert home.status_code == 200
        assert "Vidhi" in home.text

        # 2. Login as Admin / Senior Advocate
        login_res = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert login_res.status_code == 200, login_res.text
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Plug-and-Play Modules Check
        mod_res = client.get("/api/modules", headers=headers)
        assert mod_res.status_code == 200
        mods = mod_res.json()
        assert len(mods) >= 2
        mod_keys = [m["module_key"] for m in mods]
        assert "legal" in mod_keys
        assert "company_management" in mod_keys

        # 4. Company Management Module (OCR + IRD Tax + Statutory Audit)
        comp_sum = client.get("/api/company/summary", headers=headers)
        assert comp_sum.status_code == 200
        assert comp_sum.json()["counts"]["total_companies"] >= 3

        # Create a new Company with auto-generated OCR, IRD Tax & Audit tasks
        new_comp_res = client.post(
            "/api/company/entities",
            headers=headers,
            json={
                "company_name_en": "Nepal Green Energy Pvt. Ltd.",
                "company_name_np": "नेपाल ग्रीन इनर्जी प्रा.लि.",
                "company_type": "Private Limited (प्रा.लि.)",
                "ocr_registration_no": "999888/083/084",
                "registration_date_bs": "2083-07-21",
                "pan_vat_no": "619988776",
                "tax_registration_type": "VAT (मु.अ.कर)",
                "ird_office": "आन्तरिक राजस्व कार्यालय, बानेश्वर",
                "tax_clearance_upto_fy": "2081/82",
                "authorized_capital": 50000000.0,
                "paidup_capital": 25000000.0,
                "registered_address": "काठमाडौँ-१०, बानेश्वर",
                "contact_person": "सुमन थापा",
                "contact_phone": "9851223344",
                "current_auditor_name": "CA प्रकाश खतिवडा",
                "auditor_ican_no": "ICAN-COP-1142",
                "annual_retainer_fee": 150000.0,
                "paid_retainer_amount": 50000.0,
                "auto_generate_periodic_tasks": True,
            },
        )
        assert new_comp_res.status_code == 200, new_comp_res.text
        comp_data = new_comp_res.json()
        comp_id = comp_data["id"]
        assert comp_data["total_activities_count"] == 6
        assert comp_data["due_retainer_amount"] == 100000.0

        # Create a custom IRD Tax Clearance Activity & mark Completed
        act_res = client.post(
            "/api/company/activities",
            headers=headers,
            json={
                "company_id": comp_id,
                "category": "IRD_TAX",
                "activity_type": "Tax Clearance Certificate (कर चुक्ता प्रमाणपत्र)",
                "fiscal_year": "2082/83",
                "due_date_bs": "2083-08-15",
                "status": "Completed / Cleared (सम्पन्न / चुक्ता)",
                "reference_or_certificate_no": "TCC-2082-83-777",
            },
        )
        assert act_res.status_code == 200, act_res.text

        # Verify parent company's tax_clearance_upto_fy updated automatically to 2082/83
        comp_detail = client.get(f"/api/company/entities/{comp_id}", headers=headers).json()
        assert comp_detail["tax_clearance_upto_fy"] == "2082/83"

        # Cleanup test company
        del_comp = client.delete(f"/api/company/entities/{comp_id}", headers=headers)
        assert del_comp.status_code == 200
