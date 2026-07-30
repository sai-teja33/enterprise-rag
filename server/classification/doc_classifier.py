import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from core.config import settings

logger = logging.getLogger(__name__)

llm = ChatOpenAI(
    model=settings.OPENAI_CHAT_MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0
)

ALLOWED_DOC_TYPES = [
    "employee_handbook",
    "leave_policy",
    "insurance_policy",
    "medical_policy",
    "travel_policy",
    "code_of_conduct",
    "work_from_home_policy",
    "performance_review_policy",
    "performance_management_policy",
    "probation_notice_policy",
    "benefits_policy",
    "payroll_policy",
    "grievance_policy",
    "security_policy",
    "it_security_policy",
    "password_mfa_policy",
    "software_installation_policy",
    "onboarding_policy",
    "offboarding_policy",
    "onboarding_offboarding_policy",
    "unknown"
]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an HR document classifier.

Your task is to classify the uploaded HR document into EXACTLY ONE of these values:

employee_handbook
leave_policy
insurance_policy
medical_policy
travel_policy
code_of_conduct
work_from_home_policy
performance_review_policy
performance_management_policy
probation_notice_policy
benefits_policy
payroll_policy
grievance_policy
security_policy
it_security_policy
password_mfa_policy
software_installation_policy
onboarding_policy
offboarding_policy
onboarding_offboarding_policy
unknown

Rules:

- Return ONLY one label.
- No explanation.
- No punctuation.
- No markdown.
"""
        ),
        (
            "human",
            """
Filename:
{file_name}

Document Preview:

{preview}
"""
        )
    ]
)


def classify_document(file_name: str, preview: str) -> str:

    chain = prompt | llm

    result = chain.invoke(
        {
            "file_name": file_name,
            "preview": preview
        }
    )

    doc_type = result.content.strip().lower()

    if doc_type not in ALLOWED_DOC_TYPES:
        logger.warning(
            "Document classifier returned unsupported type '%s' for file '%s' and will fall back to unknown.",
            doc_type,
            file_name,
        )
        return "unknown"

    if doc_type == "unknown":
        logger.warning(
            "Document classifier returned 'unknown' for file '%s'. Review the document or add a new HR category if needed.",
            file_name,
        )

    return doc_type