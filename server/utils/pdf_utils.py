from pypdf import PdfReader


def extract_preview_text(pdf_path: str, max_pages: int = 2) -> str:
    """
    Extract text from the first few pages of a PDF.
    Used only for document classification.
    """

    reader = PdfReader(pdf_path)

    text = []

    for page in reader.pages[:max_pages]:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)

    preview = "\n".join(text)

    # limit size sent to LLM
    return preview[:2500]