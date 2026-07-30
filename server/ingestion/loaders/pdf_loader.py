import re

import fitz  # PyMuPDF
from langchain_core.documents import Document


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text while preserving paragraph structure.
    """

    if not text:
        return ""

    text = text.replace("\r", "\n")

    text = "\n".join(line.rstrip() for line in text.splitlines())

    text = re.sub(r"[ \t]{2,}", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def looks_like_table(text: str) -> bool:
    """
    Lightweight heuristic for detecting simple tables.
    """

    if not text:
        return False

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if len(lines) < 2:
        return False

    score = 0

    for line in lines:

        if line.count("|") >= 2:
            score += 2

        if re.search(r"\s{3,}", line):
            score += 1

        if "\t" in line:
            score += 1

    return score >= 2


def looks_like_list(text: str) -> bool:
    """
    Detect bulleted and numbered lists.
    """

    if not text:
        return False

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if len(lines) < 2:
        return False

    bullet_pattern = re.compile(
        r"^(?:[-*•▪◦●]|[0-9]+[.)]|[a-zA-Z][.)])\s+"
    )

    matches = sum(
        1
        for line in lines
        if bullet_pattern.match(line)
    )

    return matches >= max(2, len(lines) // 2)


def get_element_type(text: str) -> str:
    """
    Determine the semantic type of a text block.
    Priority:
    table > list > paragraph
    """

    if looks_like_table(text):
        return "table"

    if looks_like_list(text):
        return "list"

    return "paragraph"


def load_pdf(file_path: str, base_metadata: dict | None = None) -> list[Document]:
    """
    Load PDF as ONE LangChain Document PER PAGE.
    Preserves block metadata for heading detection.
    """

    base_metadata = base_metadata or {}

    print("\nUSING PDF LOADER:", __file__)

    pdf = fitz.open(file_path)

    documents = []

    for page_index in range(len(pdf)):

        page = pdf.load_page(page_index)
        page_dict = page.get_text("dict")

        page_blocks = []
        page_text_parts = []

        block_number = 0

        for block in page_dict["blocks"]:

            if block.get("type") != 0:
                continue

            block_text = []
            spans_metadata = []

            max_font_size = 0
            has_bold = False

            for line in block.get("lines", []):

                line_text = []

                for span in line.get("spans", []):

                    text = span.get("text", "").strip()

                    if not text:
                        continue

                    line_text.append(text)

                    font_size = float(span.get("size", 0))
                    font_name = span.get("font", "")

                    max_font_size = max(max_font_size, font_size)

                    if "bold" in font_name.lower():
                        has_bold = True

                    spans_metadata.append(
                        {
                            "text": text,
                            "font": font_name,
                            "size": font_size,
                            "flags": span.get("flags", 0),
                            "bbox": span.get("bbox"),
                        }
                    )

                if line_text:
                    block_text.append(" ".join(line_text))

            text = clean_text("\n".join(block_text))

            if not text:
                continue

            page_text_parts.append(text)

            page_blocks.append(
                {
                    "block_number": block_number,
                    "text": text,
                    "element_type": get_element_type(text),
                    "max_font_size": max_font_size,
                    "is_bold": has_bold,
                    "text_spans": spans_metadata,
                }
            )

            block_number += 1

        if not page_text_parts:
            continue

        page_text = "\n\n".join(page_text_parts)

        metadata = {
            **base_metadata,
            "page_number": page_index + 1,
            "page_start": page_index + 1,
            "page_end": page_index + 1,
            "source_file": file_path,
            "page_width": page.rect.width,
            "page_height": page.rect.height,
            "block_count": len(page_blocks),
            "blocks": page_blocks,
        }

        documents.append(
            Document(
                page_content=page_text,
                metadata=metadata,
            )
        )

    print("Returning documents:", len(documents))

    pdf.close()

    return documents