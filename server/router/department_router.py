import re
import json
from llm.answer_generator import call_llm

HR_KEYWORDS = {
    "leave",
    "sick",
"casual",
"earned",
"annual",
"vacation",
    "attendance",
    "salary",
    "payroll",
    "insurance",
    "medical",
    "benefits",
    "holiday",
    "vacation",
    "employee",
    "promotion",
    "performance",
    "joining",
    "onboarding",
    "offboarding",
    "probation",
    "notice",
    "resignation",
    "gratuity",
    "pf",
    "claim",
    "reimbursement",
    "travel",
    "wellness",
    "maternity",
    "paternity",
    "bereavement",
    "policy",
    "hr"
}

IT_KEYWORDS = {
    "vpn",
    "wifi",
    "password",
    "login",
    "email",
    "vpn",
"wifi",
"reset",
"credential",
"account",
    "outlook",
    "laptop",
    "desktop",
    "monitor",
    "printer",
    "software",
    "application",
    "install",
    "installation",
    "github",
    "git",
    "docker",
    "jira",
    "aws",
    "azure",
    "server",
    "network",
    "internet",
    "ssh",
    "access",
    "mfa",
    "authentication",
    "firewall",
    "windows",
    "linux"
}
def tokenize(text: str) -> set[str]:
    tokens = re.findall(r"\b[a-zA-Z]+\b", text.lower())

    normalized = set()

    for token in tokens:
        if token.endswith("ies"):
            token = token[:-3] + "y"
        elif token.endswith("es") and len(token) > 4:
            token = token[:-2]
        elif token.endswith("s") and len(token) > 3:
            token = token[:-1]

        normalized.add(token)

    return normalized

def keyword_router(question: str) -> dict:
    tokens = tokenize(question)

    hr_matches = tokens.intersection(HR_KEYWORDS)
    it_matches = tokens.intersection(IT_KEYWORDS)

    hr_score = len(hr_matches)
    it_score = len(it_matches)

    if hr_score == 0 and it_score == 0:
        return {
            "department": "unknown",
            "method": "keyword",
            "confidence": 0.0,
            "reason": "No keyword match"
        }

    if hr_score > it_score:
        return {
            "department": "hr",
            "method": "keyword",
            "confidence": 1.0,
            "reason": f"Matched HR keywords: {sorted(hr_matches)}"
        }

    if it_score > hr_score:
        return {
            "department": "it",
            "method": "keyword",
            "confidence": 1.0,
            "reason": f"Matched IT keywords: {sorted(it_matches)}"
        }

    return {
        "department": "unknown",
        "method": "keyword",
        "confidence": 0.0,
        "reason": "Equal keyword score"
    }

DEPARTMENT_ROUTER_SYSTEM_PROMPT = """
You are an enterprise department classifier.

Available departments:
- hr
- it

You MUST return ONLY valid JSON.

Example:

{
    "department":"hr",
    "confidence":0.98,
    "reason":"Question is about employee leave."
}

or

{
    "department":"it",
    "confidence":0.97,
    "reason":"Question is about VPN."
}

Do not return markdown.
Do not return explanations.
Do not use ```json.
Only output JSON.
"""
def build_router_prompt(question: str) -> str:
    return f"""
Question:

{question}
"""
def llm_router(question: str):

    raw_response = call_llm(
        DEPARTMENT_ROUTER_SYSTEM_PROMPT,
        build_router_prompt(question)
    )

    try:
        cleaned = raw_response.strip()

        if cleaned.startswith("```"):
             cleaned = cleaned.replace("```json", "")
             cleaned = cleaned.replace("```", "").strip()

        parsed = json.loads(cleaned)

        return {
            "department": parsed["department"],
            "method": "llm",
            "confidence": parsed.get("confidence", 0.9),
            "reason": parsed.get("reason", "")
        }

    except Exception:

        return {
            "department": "unknown",
            "method": "llm",
            "confidence": 0,
            "reason": "Failed to parse LLM output"
        }
def route_department(question: str):

    keyword_result = keyword_router(question)

    if keyword_result["department"] != "unknown":
        return keyword_result

    return llm_router(question)
if __name__ == "__main__":

    questions = [

        "How many sick leaves are allowed?",

        "My VPN password is not working.",

        "Tell me about maternity leave.",

        "Docker installation failed.",

        "I need approval."

    ]

    for q in questions:

        print("=" * 70)
        print(q)

        result = route_department(q)

        print(result)