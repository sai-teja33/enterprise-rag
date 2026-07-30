import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

from chunking.heading_utils import (
    split_text_into_sections,
    merge_small_sections,
)

# Embedding model used throughout the project
EMBEDDING_MODEL = "text-embedding-3-small"

DEFAULT_CHUNK_SIZE = 500      # tokens
DEFAULT_CHUNK_OVERLAP = 75    # tokens

# Tokenizer (can also be used elsewhere if needed)
encoding = tiktoken.encoding_for_model(EMBEDDING_MODEL)


def get_splitter(
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
):
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name=EMBEDDING_MODEL,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


def recursive_chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict]:

    splitter = get_splitter(chunk_size, chunk_overlap)

    pieces = splitter.split_text(text or "")

    chunks = []

    for piece in pieces:

        piece = piece.strip()

        if not piece:
            continue

        chunks.append(
            {
                "chunk_text": piece,
                "page_start": None,
                "page_end": None,
                "section_title": None,
                "token_count": len(encoding.encode(piece)),
                "chunking_strategy": "recursive",
            }
        )

    return chunks

def section_recursive_chunk_docs(docs: list) -> list[dict]:
    """
    Split page -> sections -> merge small sections -> recursive token chunks.
    """

    splitter = get_splitter()

    all_chunks = []

    for doc in docs:

        text = doc.page_content or ""
        metadata = doc.metadata or {}

        if not text.strip():
            continue

        page_start = metadata.get("page_start")
        page_end = metadata.get("page_end")

        # Backward compatibility
        if page_start is None:
            page_start = metadata.get("page_number")

        if page_end is None:
            page_end = page_start

        sections = split_text_into_sections(text, blocks=metadata.get("blocks"))
        sections = merge_small_sections(sections)

        for section in sections:

            section_title = section["section_title"]
            section_text = section["section_text"]

            pieces = splitter.split_text(section_text)

            for piece in pieces:

                piece = piece.strip()

                if not piece:
                    continue

                if section_title:

                    if piece.startswith(section_title):
                        chunk_text = piece
                    else:
                        chunk_text = f"{section_title}\n\n{piece}"

                else:
                    chunk_text = piece

                all_chunks.append(
                    {
                        "chunk_text": chunk_text,
                        "page_start": page_start,
                        "page_end": page_end,
                        "section_title": section["section_title"],
                        "parent_section": section["parent_section"],
                        "heading_level": section["heading_level"],
                        "element_type": metadata.get(
                            "element_type",
                            section["element_type"],
                        ),
                        "token_count": len(encoding.encode(chunk_text)),
                        "chunking_strategy": "section_recursive",
                    }
                )

    return all_chunks

def page_section_recursive_chunk_docs(docs: list) -> list[dict]:
    """
    Page-aware recursive token chunking.
    """

    splitter = get_splitter()

    all_chunks = []

    for doc in docs:

        text = doc.page_content or ""
        metadata = doc.metadata or {}

        if not text.strip():
            continue

        page_start = metadata.get("page_start")
        page_end = metadata.get("page_end")

        if page_start is None:
            page_start = metadata.get("page_number")

        if page_end is None:
            page_end = page_start

        sections = split_text_into_sections(text, blocks=metadata.get("blocks"))
        sections = merge_small_sections(sections)

        for section in sections:

            section_title = section["section_title"]
            section_text = section["section_text"]

            pieces = splitter.split_text(section_text)

            for piece in pieces:

                piece = piece.strip()

                if not piece:
                    continue

                if section_title:

                    if piece.startswith(section_title):
                        chunk_text = piece
                    else:
                        chunk_text = f"{section_title}\n\n{piece}"

                else:
                    chunk_text = piece

                all_chunks.append(
                    {
                        "chunk_text": chunk_text,
                        "page_start": page_start,
                        "page_end": page_end,
                        "section_title": section["section_title"],
                        "parent_section": section["parent_section"],
                        "heading_level": section["heading_level"],
                        "element_type": metadata.get(
                            "element_type",
                            section["element_type"],
                        ),
                        "token_count": len(encoding.encode(chunk_text)),
                        "chunking_strategy": "page_section_recursive",
                    }
                )

    return all_chunks