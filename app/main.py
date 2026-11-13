from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, SessionLocal, get_db, upgrade_schema_for_multitenancy
from app.models import PaymentRecord, LegalCase, Tenant
from app.seed import seed_initial_data
from app.routers import (
    auth_router,
    tenants_router,
    staff_router,
    clients_router,
    cases_router,
    hearings_router,
    finance_router,
    documents_router,
    dashboard_router,
    modules_router,
    company_router,
)
from app.routers.finance_router import serialize_payment
from app.routers.cases_router import serialize_case

APP_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    upgrade_schema_for_multitenancy()
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Enterprise Multi-Tenant Law Firm, OCR, IRD Tax & Audit Management System (विधि तथा कर्पोरेट बहु-टेनेन्ट प्रणाली)"
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

# Include API Routers
app.include_router(auth_router.router)
app.include_router(tenants_router.router)
app.include_router(modules_router.router)
app.include_router(dashboard_router.router)
app.include_router(clients_router.router)
app.include_router(cases_router.router)
app.include_router(hearings_router.router)
app.include_router(finance_router.router)
app.include_router(documents_router.router)
app.include_router(company_router.router)
app.include_router(staff_router.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/print/receipt/{payment_id}", response_class=HTMLResponse, tags=["Printable Reports"])
def print_receipt_view(payment_id: int, request: Request, db: Session = Depends(get_db)):
    payment = db.query(PaymentRecord).filter(PaymentRecord.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="रसिद भेटिएन (Receipt not found)")
    tenant = db.query(Tenant).filter(Tenant.id == payment.tenant_id).first()
    serialized = serialize_payment(payment)
    return templates.TemplateResponse(
        request,
        "receipt_print.html",
        {"payment": serialized, "tenant": tenant},
    )


@app.get("/print/case/{case_id}", response_class=HTMLResponse, tags=["Printable Reports"])
def print_case_dossier_view(case_id: int, request: Request, db: Session = Depends(get_db)):
    legal_case = db.query(LegalCase).filter(LegalCase.id == case_id).first()
    if not legal_case:
        raise HTTPException(status_code=404, detail="मुद्दाको विवरण भेटिएन (Case not found)")
    tenant = db.query(Tenant).filter(Tenant.id == legal_case.tenant_id).first()
    serialized = serialize_case(legal_case, include_details=True)
    return templates.TemplateResponse(
        request,
        "case_print.html",
        {"case": serialized, "tenant": tenant},
    )


@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "system": settings.PROJECT_NAME,
        "architecture": "Enterprise Multi-Tenant SaaS",
        "database_driver": engine.url.drivername,
        "database_name": engine.url.database,
    }
