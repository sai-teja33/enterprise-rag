from chunking.strategies import (
    recursive_chunk_text,
    section_recursive_chunk_docs,
    page_section_recursive_chunk_docs
)


DOC_TYPE_TO_CHUNKING = {
    "leave_policy": "section_recursive",
    "insurance_policy": "section_recursive",
    "medical_policy": "section_recursive",
    "travel_policy": "section_recursive",
    "code_of_conduct": "section_recursive",
    "work_from_home_policy": "section_recursive",
    "performance_review_policy": "section_recursive",
    "performance_management_policy": "section_recursive",
    "probation_notice_policy": "section_recursive",
    "benefits_policy": "section_recursive",
    "payroll_policy": "section_recursive",
    "grievance_policy": "section_recursive",
    "security_policy": "section_recursive",
    "it_security_policy": "section_recursive",
    "password_mfa_policy": "section_recursive",
    "software_installation_policy": "section_recursive",
    "onboarding_policy": "section_recursive",
    "offboarding_policy": "section_recursive",
    "onboarding_offboarding_policy": "section_recursive",
    "employee_handbook": "page_section_recursive",
    "unknown": "section_recursive"
}


def choose_chunking_strategy(doc_type: str | None) -> str:
    if not doc_type:
        return "section_recursive"
    return DOC_TYPE_TO_CHUNKING.get(doc_type.lower(), "section_recursive")


def chunk_loaded_documents(
    docs: list,
    doc_type: str | None
) -> tuple[str, list[dict]]:
    """
    Input:
      docs = LangChain documents returned by load_document(...)

    Returns:
      (strategy_name, chunks)

    chunk format:
    [
      {
        "chunk_text": "...",
        "page_number": 1,
        "section_title": "Leave Policy",
        "chunking_strategy": "section_recursive"
      }
    ]
    """
    strategy = choose_chunking_strategy(doc_type)

    if strategy == "page_section_recursive":
        chunks = page_section_recursive_chunk_docs(docs)

    else:
        chunks = section_recursive_chunk_docs(docs)

    if not chunks:
        full_text = "\n\n".join(doc.page_content for doc in docs if doc.page_content)
        chunks = recursive_chunk_text(full_text)
        strategy = "recursive"

    return strategy, chunks