from datetime import datetime
from db.mongo import departments_collection


def create_department(name: str, slug: str, description: str | None = None):
    existing = departments_collection.find_one({"slug": slug})
    if existing:
        return None

    department_doc = {
        "name": name,
        "slug": slug,
        "description": description,
        "created_at": datetime.utcnow()
    }

    result = departments_collection.insert_one(department_doc)

    department_doc["_id"] = result.inserted_id
    return department_doc


def get_all_departments():
    return list(
        departments_collection.find().sort("created_at", -1)
    )


def get_department_by_slug(slug: str):
    return departments_collection.find_one({"slug": slug})