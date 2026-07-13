from pypdf import PdfReader
from langchain_core.documents import Document


def load_pdf(file_path: str, base_metadata: dict | None = None) -> list[Document]:
    reader = PdfReader(file_path)
    documents = []

    base_metadata = base_metadata or {}

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()

        if not text:
            continue

        metadata = {
            **base_metadata,
            "page_number": i,
            "source_file": file_path
        }

        documents.append(
            Document(
                page_content=text,
                metadata=metadata
            )
        )

    return documents