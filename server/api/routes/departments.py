from fastapi import APIRouter, HTTPException

from models.department import DepartmentCreate, DepartmentResponse
from db.repositories.department_repo import (
    create_department,
    get_all_departments
)

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("", response_model=DepartmentResponse)
def create_department_api(payload: DepartmentCreate):
    department = create_department(
        payload.name,
        payload.slug,
        payload.description
    )

    if department is None:
        raise HTTPException(
            status_code=400,
            detail="Department with this slug already exists"
        )

    return DepartmentResponse(
        id=str(department["_id"]),
        name=department["name"],
        slug=department["slug"],
        description=department.get("description"),
        created_at=department["created_at"]
    )


@router.get("", response_model=list[DepartmentResponse])
def list_departments_api():
    departments = get_all_departments()

    return [
        DepartmentResponse(
            id=str(d["_id"]),
            name=d["name"],
            slug=d["slug"],
            description=d.get("description"),
            created_at=d["created_at"]
        )
        for d in departments
    ]