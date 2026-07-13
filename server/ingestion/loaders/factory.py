import os
from langchain_core.documents import Document
from app.ingestion.loaders.pdf_loader import load_pdf
from app.ingestion.loaders.docx_loader import load_docx


def load_document(file_path: str, base_metadata: dict | None = None) -> list[Document]:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return load_pdf(file_path, base_metadata=base_metadata)
    elif ext == ".docx":
        return load_docx(file_path, base_metadata=base_metadata)
    else:
        raise ValueError(f"Unsupported file type: {ext}")