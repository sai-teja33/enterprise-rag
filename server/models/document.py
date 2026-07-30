from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    id: str
    title: str
    doc_type: str
    file_name: str
    file_path: str
    uploaded_at: datetime