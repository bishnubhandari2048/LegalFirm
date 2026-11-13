from fastapi.testclient import TestClient
from app.main import app


def test_full_law_firm_company_and_mdm_workflow():
    with TestClient(app) as client:
        # 1. Health & UI Home
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

        home = client.get("/")
        assert home.status_code == 200
        assert "Vidhi" in home.text

        # 2. Login as Admin / Senior Advocate (Tenant #1 + SaaS Host SuperAdmin)
        login_res = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert login_res.status_code == 200, login_res.text
        user_info = login_res.json()["user"]
        assert user_info["tenant_id"] == 1
        assert user_info["tenant"]["tenant_code"] == "VIDHI-001"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Verify MDM (Master Data Management) for Adalat List, Mudda ko Prakriti, etc.
        tenant_ctx = client.get("/api/tenants/current", headers=headers)
        assert tenant_ctx.status_code == 200
        lovs = tenant_ctx.json()["lovs"]
        assert len(lovs.get("COURT_NAME", [])) >= 15  # Adalat List
        assert len(lovs.get("CASE_TYPE", [])) >= 12   # Mudda ko Prakriti
        assert len(lovs.get("HEARING_STATUS", [])) >= 8
        assert len(lovs.get("CASE_STATUS", [])) >= 5
        assert len(lovs.get("PARTY_ROLE", [])) >= 5
        assert len(lovs.get("DOCUMENT_TYPE", [])) >= 4
        assert len(lovs.get("PAYMENT_METHOD", [])) >= 5
        assert len(lovs.get("COMPANY_TYPE", [])) >= 4
        assert len(lovs.get("IRD_OFFICE", [])) >= 10

        # 4. Plug-and-Play Modules Check
        mod_res = client.get("/api/modules", headers=headers)
        assert mod_res.status_code == 200
        mods = mod_res.json()
        assert len(mods) >= 2
        mod_keys = [m["module_key"] for m in mods]
        assert "legal" in mod_keys
        assert "company_management" in mod_keys

        # 5. Create a new Company with auto-generated OCR, IRD Tax & Audit tasks
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


def test_enterprise_multitenant_isolation_and_security():
    """Verify strict multi-tenant data isolation, zero-selection tenant login, and per-tenant MDM/LOVs."""
    with TestClient(app) as client:
        # 1. Login as Tenant 1 (admin)
        t1_login = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert t1_login.status_code == 200
        t1_headers = {"Authorization": f"Bearer {t1_login.json()['access_token']}"}
        t1_tenant_id = t1_login.json()["user"]["tenant_id"]
        assert t1_tenant_id == 1

        # 2. Login as Tenant 2 (apex_admin) — Zero tenant selection on login!
        t2_login = client.post(
            "/api/auth/login",
            json={"username": "apex_admin", "password": "lawfirm123"},
        )
        assert t2_login.status_code == 200, t2_login.text
        t2_user = t2_login.json()["user"]
        t2_tenant_id = t2_user["tenant_id"]
        assert t2_tenant_id != t1_tenant_id
        assert t2_user["tenant"]["tenant_code"] == "APEX-002"
        t2_headers = {"Authorization": f"Bearer {t2_login.json()['access_token']}"}

        # 3. Register a confidential Client in Tenant 1
        t1_client_res = client.post(
            "/api/clients",
            headers=t1_headers,
            json={
                "first_name": "Confidential",
                "last_name": "TenantOneClient",
                "address": "Baluwatar, Kathmandu",
                "phone": "9851999999",
                "email": "secret@tenant1.com",
                "citizenship_no": "T1-SECRET-9999",
            },
        )
        assert t1_client_res.status_code == 200
        t1_client_id = t1_client_res.json()["id"]
        assert t1_client_res.json()["tenant_id"] == t1_tenant_id

        # 4. Verify Tenant 2 CANNOT access or view Tenant 1's Client
        t2_get_t1_client = client.get(f"/api/clients/{t1_client_id}", headers=t2_headers)
        assert t2_get_t1_client.status_code == 404

        t2_clients_list = client.get("/api/clients", headers=t2_headers).json()
        assert all(c["id"] != t1_client_id for c in t2_clients_list)
        assert all(c["tenant_id"] == t2_tenant_id for c in t2_clients_list)

        # Verify Tenant 2's Conflict Check does NOT leak Tenant 1's Client
        t2_conflict = client.get(
            "/api/dashboard/conflict-check?q=T1-SECRET-9999",
            headers=t2_headers,
        ).json()
        assert t2_conflict["has_conflict"] is False

        # Verify Tenant 2 cannot update or delete Tenant 1's Client
        assert (
            client.put(
                f"/api/clients/{t1_client_id}",
                headers=t2_headers,
                json={"address": "Hacked"},
            ).status_code
            == 404
        )
        assert client.delete(f"/api/clients/{t1_client_id}", headers=t2_headers).status_code == 404

        # 5. Verify Tenant-Scoped MDM/LOVs: Add custom Court in Tenant 2 and confirm Tenant 1 does not see it
        t2_lov_res = client.post(
            "/api/tenants/lov",
            headers=t2_headers,
            json={
                "lov_group": "COURT",
                "label_en": "Pokhara High Court Commercial Bench (Apex Custom)",
                "label_np": "उच्च अदालत पोखरा वाणिज्य इजलास",
            },
        )
        assert t2_lov_res.status_code == 200
        lov_id = t2_lov_res.json()["id"]

        t1_courts = client.get("/api/tenants/lov?lov_group=COURT", headers=t1_headers).json()
        assert all(item["id"] != lov_id for item in t1_courts)

        # Cleanup custom LOV and confidential client
        assert client.delete(f"/api/tenants/lov/{lov_id}", headers=t2_headers).status_code == 200
        assert client.delete(f"/api/clients/{t1_client_id}", headers=t1_headers).status_code == 200
