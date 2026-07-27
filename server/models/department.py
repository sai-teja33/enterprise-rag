from pydantic import BaseModel, Field
from datetime import datetime


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50)
    description: str | None = None


class DepartmentResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None = None
    created_at: datetime