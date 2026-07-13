import re

STOPWORDS = {
    "what", "is", "the", "are", "a", "an", "of", "for", "to", "in", "on",
    "how", "many", "can", "be", "does", "do", "with", "and", "or", "by",
    "company", "employee", "employees", "policy", "policies"
}


def normalize_tokens(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-zA-Z]+", text)
    return [t for t in tokens if len(t) > 2 and t not in STOPWORDS]


def lexical_overlap_score(question: str, chunks: list[dict]) -> dict:
    question_tokens = set(normalize_tokens(question))

    if not question_tokens:
        return {
            "question_tokens": [],
            "matched_tokens": [],
            "coverage_ratio": 0.0
        }

    combined_text = " ".join(chunk.get("chunk_text", "") for chunk in chunks).lower()
    matched_tokens = sorted([token for token in question_tokens if token in combined_text])

    coverage_ratio = len(matched_tokens) / len(question_tokens)

    return {
        "question_tokens": sorted(question_tokens),
        "matched_tokens": matched_tokens,
        "coverage_ratio": coverage_ratio
    }