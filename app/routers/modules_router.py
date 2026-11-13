from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SystemModuleConfig, StaffMember
from app.schemas import ModuleConfigUpdate
from app.auth import get_current_user, get_current_tenant_id
from app.routers.tenants_router import provision_tenant_defaults

router = APIRouter(prefix="/api/modules", tags=["Plug-and-Play Modules / मोड्युल व्यवस्थापन"])


def serialize_module(m: SystemModuleConfig) -> dict:
    return {
        "id": m.id,
        "tenant_id": m.tenant_id,
        "module_key": m.module_key,
        "name_en": m.name_en,
        "name_np": m.name_np,
        "description_en": m.description_en or "",
        "description_np": m.description_np or "",
        "is_enabled": m.is_enabled,
        "enable_ocr": m.enable_ocr,
        "enable_ird_tax": m.enable_ird_tax,
        "enable_audit": m.enable_audit,
        "plan_tier": m.plan_tier or "Enterprise",
    }


@router.get("")
def list_modules(
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    modules = (
        db.query(SystemModuleConfig)
        .filter(SystemModuleConfig.tenant_id == tenant_id)
        .order_by(SystemModuleConfig.id.asc())
        .all()
    )
    if not modules:
        provision_tenant_defaults(tenant_id, db)
        db.commit()
        modules = (
            db.query(SystemModuleConfig)
            .filter(SystemModuleConfig.tenant_id == tenant_id)
            .order_by(SystemModuleConfig.id.asc())
            .all()
        )
    return [serialize_module(m) for m in modules]


@router.put("/{module_key}")
def update_module_subscription(
    module_key: str,
    payload: ModuleConfigUpdate,
    db: Session = Depends(get_db),
    current_user: StaffMember = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
):
    mod = (
        db.query(SystemModuleConfig)
        .filter(
            SystemModuleConfig.tenant_id == tenant_id,
            SystemModuleConfig.module_key == module_key,
        )
        .first()
    )
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found for this tenant")

    mod.is_enabled = payload.is_enabled
    if payload.enable_ocr is not None:
        mod.enable_ocr = payload.enable_ocr
    if payload.enable_ird_tax is not None:
        mod.enable_ird_tax = payload.enable_ird_tax
    if payload.enable_audit is not None:
        mod.enable_audit = payload.enable_audit
    if payload.plan_tier:
        mod.plan_tier = payload.plan_tier

    db.commit()
    db.refresh(mod)
    return serialize_module(mod)
