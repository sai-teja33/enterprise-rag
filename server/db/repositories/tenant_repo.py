from datetime import datetime
from app.db.mongo import tenants_collection


def create_tenant(name: str, slug: str):
    existing = tenants_collection.find_one({"slug": slug})
    if existing:
        return None

    tenant_doc = {
        "name": name,
        "slug": slug,
        "created_at": datetime.utcnow()
    }

    result = tenants_collection.insert_one(tenant_doc)

    tenant_doc["_id"] = result.inserted_id
    return tenant_doc


def get_all_tenants():
    return list(tenants_collection.find().sort("created_at", -1))