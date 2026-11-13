"""
Clear All Transactional Data & Ensure Master Data Management (MDM) Lists
========================================================================
Usage:
  Local:
    python scripts/clear_transactional_data.py
    python scripts/clear_transactional_data.py --clean-demo-users

  Production VPS (Docker):
    docker compose -f docker-compose.prod.yml exec app python scripts/clear_transactional_data.py --clean-demo-users

What gets DELETED (Transactional Data):
  - hearings              (पेशी तथा तारेख विवरण)
  - payment_records       (आर्थिक तथा रसिद विवरण)
  - case_documents        (कागजात सम्बन्धी विवरण)
  - legal_cases           (मुद्दाको विवरण)
  - compliance_activities (आवधिक OCR / कर / लेखापरीक्षण कार्य)
  - corporate_entities    (दर्ता गरिएका क्लाइन्ट कम्पनीहरू)
  - clients               (क्लाइन्टको विवरण)

What is PRESERVED & SEEDED (Master Data / MDM & Configuration):
  - tenants               (फर्म / टेनेन्ट विवरण)
  - staff_members         (प्रशासक / वकिल खाताहरू — or only Admin accounts with --clean-demo-users)
  - system_module_configs (प्लग-एण्ड-प्ले मोड्युल सेटिङ)
  - tenant_lovs           (MDM Master Data: Adalat List / अदालतको सूची, Mudda ko Prakriti / मुद्दाको प्रकृति,
                           Peshi Status, Case Status, Party Role, Document Type, Payment Method,
                           Company Type, IRD Offices)
"""

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import text
from app.database import Base, engine, SessionLocal, upgrade_schema_for_multitenancy
from app.models import (
    Tenant,
    TenantLOV,
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
from app.seed import ensure_multitenant_foundation
from app.routers.tenants_router import provision_tenant_defaults

TRANSACTIONAL_TABLES = [
    "hearings",
    "payment_records",
    "case_documents",
    "legal_cases",
    "compliance_activities",
    "corporate_entities",
    "clients",
]


def clear_all_transactional_data(clean_demo_users: bool = False, tenant_id: int | None = None):
    print("======================================================================")
    print(" Vidhi CMS — Clearing Transactional Data & Refreshing MDM Master Data")
    print("======================================================================")

    Base.metadata.create_all(bind=engine)
    upgrade_schema_for_multitenancy()
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if tenant_id is not None:
            print(f"-> Clearing transactional records for Tenant ID = {tenant_id} ...")
            db.query(Hearing).filter(Hearing.tenant_id == tenant_id).delete(synchronize_session=False)
            db.query(PaymentRecord).filter(PaymentRecord.tenant_id == tenant_id).delete(synchronize_session=False)
            db.query(CaseDocument).filter(CaseDocument.tenant_id == tenant_id).delete(synchronize_session=False)
            db.query(LegalCase).filter(LegalCase.tenant_id == tenant_id).delete(synchronize_session=False)
            db.query(ComplianceActivity).filter(ComplianceActivity.tenant_id == tenant_id).delete(synchronize_session=False)
            db.query(CorporateEntity).filter(CorporateEntity.tenant_id == tenant_id).delete(synchronize_session=False)
            db.query(Client).filter(Client.tenant_id == tenant_id).delete(synchronize_session=False)
            db.commit()
        else:
            print("-> Clearing all transactional tables across database...")
            db.query(Hearing).delete(synchronize_session=False)
            db.query(PaymentRecord).delete(synchronize_session=False)
            db.query(CaseDocument).delete(synchronize_session=False)
            db.query(LegalCase).delete(synchronize_session=False)
            db.query(ComplianceActivity).delete(synchronize_session=False)
            db.query(CorporateEntity).delete(synchronize_session=False)
            db.query(Client).delete(synchronize_session=False)
            db.commit()

            # Reset AUTO_INCREMENT on MySQL so new production records start at ID 1
            if "mysql" in engine.url.drivername:
                with engine.begin() as conn:
                    for tbl in TRANSACTIONAL_TABLES:
                        try:
                            conn.execute(text(f"ALTER TABLE {tbl} AUTO_INCREMENT = 1"))
                        except Exception:
                            pass

        if clean_demo_users:
            print("-> Removing demo non-admin staff accounts (sunita, dipak, kamal, asmita)...")
            db.query(StaffMember).filter(
                StaffMember.username.in_(["sunita", "dipak", "kamal", "asmita"])
            ).delete(synchronize_session=False)
            db.commit()

        # Ensure Tenants, Admin Accounts, Plug-and-Play Modules, and Full MDM Catalog exist
        print("-> Ensuring Tenants, Admin Accounts, Modules & MDM (Adalat List, Mudda ko Prakriti, etc.)...")
        ensure_multitenant_foundation(db)

        all_tenants = db.query(Tenant).all()
        for t in all_tenants:
            provision_tenant_defaults(t, db, force_missing_mdm=True)
        db.commit()

        # Summary report
        print("\n[SUCCESS] Transactional data cleared and Master Data (MDM) verified!")
        print("----------------------------------------------------------------------")
        print(f"  Clients (Transactional)            : {db.query(Client).count()}")
        print(f"  Court Cases (Transactional)        : {db.query(LegalCase).count()}")
        print(f"  Hearings / Peshi (Transactional)   : {db.query(Hearing).count()}")
        print(f"  Payments / Receipts (Transactional): {db.query(PaymentRecord).count()}")
        print(f"  Documents (Transactional)          : {db.query(CaseDocument).count()}")
        print(f"  Companies (Transactional)          : {db.query(CorporateEntity).count()}")
        print(f"  Compliance Tasks (Transactional)   : {db.query(ComplianceActivity).count()}")
        print("----------------------------------------------------------------------")
        print(f"  Tenants (Preserved)                : {db.query(Tenant).count()}")
        print(f"  Active Users (Preserved)           : {db.query(StaffMember).count()}")
        print(f"  Module Configs (Preserved)         : {db.query(SystemModuleConfig).count()}")
        print(f"  MDM / LOV Master Records (Seeded)  : {db.query(TenantLOV).count()}")
        print("======================================================================")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clear all transactional data while preserving MDM & Tenants.")
    parser.add_argument(
        "--clean-demo-users",
        action="store_true",
        help="Also delete demo staff accounts (sunita, dipak, kamal, asmita) and keep only admin accounts.",
    )
    parser.add_argument(
        "--tenant-id",
        type=int,
        default=None,
        help="Optional: Clear transactional data only for a specific tenant_id.",
    )
    args = parser.parse_args()
    clear_all_transactional_data(clean_demo_users=args.clean_demo_users, tenant_id=args.tenant_id)
