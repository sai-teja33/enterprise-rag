from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from core.config import settings

llm = ChatOpenAI(
    model=settings.OPENAI_CHAT_MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0
)

ALLOWED_DOC_TYPES = [
    "employee_handbook",
    "leave_policy",
    "insurance_policy",
    "travel_policy",
    "code_of_conduct",
    "work_from_home_policy",
    "performance_review_policy",
    "probation_notice_policy",
    "benefits_policy",
    "payroll_policy",
    "grievance_policy",
    "security_policy",
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
travel_policy
code_of_conduct
work_from_home_policy
performance_review_policy
probation_notice_policy
benefits_policy
payroll_policy
grievance_policy
security_policy
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
        return "unknown"

    return doc_type