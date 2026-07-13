from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50)


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime