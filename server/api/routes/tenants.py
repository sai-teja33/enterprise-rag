from fastapi import APIRouter, HTTPException
from models.tenant import TenantCreate, TenantResponse
from db.repositories.tenant_repo import create_tenant, get_all_tenants

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post("", response_model=TenantResponse)
def create_tenant_api(payload: TenantCreate):
    tenant = create_tenant(payload.name, payload.slug)

    if tenant is None:
        raise HTTPException(status_code=400, detail="Tenant with this slug already exists")

    return TenantResponse(
        id=str(tenant["_id"]),
        name=tenant["name"],
        slug=tenant["slug"],
        created_at=tenant["created_at"]
    )


@router.get("", response_model=list[TenantResponse])
def list_tenants_api():
    tenants = get_all_tenants()

    return [
        TenantResponse(
            id=str(t["_id"]),
            name=t["name"],
            slug=t["slug"],
            created_at=t["created_at"]
        )
        for t in tenants
    ]