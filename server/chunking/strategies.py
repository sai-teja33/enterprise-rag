from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.chunking.heading_utils import split_text_into_sections

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 120


def recursive_chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    pieces = splitter.split_text(text or "")

    return [
        {
            "chunk_text": piece,
            "page_number": None,
            "section_title": None,
            "chunking_strategy": "recursive"
        }
        for piece in pieces
        if piece.strip()
    ]


def section_recursive_chunk_docs(
    docs: list
) -> list[dict]:
    """
    Uses the already-loaded LangChain docs (often page-based for PDFs),
    groups by page, splits each page into sections, then recursively chunks section text.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP
    )

    all_chunks = []

    for doc in docs:
        text = doc.page_content or ""
        metadata = doc.metadata or {}
        page_number = metadata.get("page_number")

        if not text.strip():
            continue

        sections = split_text_into_sections(text)

        for section in sections:
            section_title = section["section_title"]
            section_text = section["section_text"]

            pieces = splitter.split_text(section_text)

            for piece in pieces:
                if piece.strip():
                    all_chunks.append({
                        "chunk_text": piece,
                        "page_number": page_number,
                        "section_title": section_title,
                        "chunking_strategy": "section_recursive"
                    })

    return all_chunks


def page_section_recursive_chunk_docs(
    docs: list
) -> list[dict]:
    """
    Similar to section_recursive, but explicitly treated as page-aware chunking.
    In practice for your current loader flow, PDFs are already page-wise LangChain docs,
    so we preserve page_number and split within each page into sections.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP
    )

    all_chunks = []

    for doc in docs:
        text = doc.page_content or ""
        metadata = doc.metadata or {}
        page_number = metadata.get("page_number")

        if not text.strip():
            continue

        sections = split_text_into_sections(text)

        for section in sections:
            section_title = section["section_title"]
            section_text = section["section_text"]

            pieces = splitter.split_text(section_text)

            for piece in pieces:
                if piece.strip():
                    all_chunks.append({
                        "chunk_text": piece,
                        "page_number": page_number,
                        "section_title": section_title,
                        "chunking_strategy": "page_section_recursive"
                    })

    return all_chunks