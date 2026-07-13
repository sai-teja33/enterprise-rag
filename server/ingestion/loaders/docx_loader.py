import docx2txt
from langchain_core.documents import Document


def load_docx(file_path: str, base_metadata: dict | None = None) -> list[Document]:
    text = docx2txt.process(file_path) or ""
    text = text.strip()

    if not text:
        return []

    base_metadata = base_metadata or {}

    metadata = {
        **base_metadata,
        "source_file": file_path
    }

    return [
        Document(
            page_content=text,
            metadata=metadata
        )
    ]