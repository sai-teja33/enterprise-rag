# import json
# from app.llm.groq_client import groq_client
# from app.llm.prompts import SYSTEM_PROMPT

# ABSTAIN_ANSWER = "I could not find a reliable answer in the uploaded tenant documents."


# def build_context(chunks: list[dict]) -> str:
#     context_parts = []

#     for idx, chunk in enumerate(chunks, start=1):
#         context_parts.append(
#             f"""[Chunk {idx}]
# Title: {chunk.get("title", "")}
# Doc Type: {chunk.get("doc_type", "")}
# File: {chunk.get("file_name", "")}
# Page: {chunk.get("page_number", "")}
# Content:
# {chunk.get("chunk_text", "")}
# """
#         )

#     return "\n\n".join(context_parts)


# def generate_grounded_answer(question: str, chunks: list[dict]) -> dict:
#     context = build_context(chunks)

#     user_prompt = f"""
# Question:
# {question}

# Context:
# {context}
# """

#     response = groq_client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": user_prompt}
#         ],
#         temperature=0
#     )

#     raw_output = response.choices[0].message.content.strip()

#     try:
#         parsed = json.loads(raw_output)

#         answer_mode = parsed.get("answer_mode", "").strip()
#         answer = parsed.get("answer", "").strip()
#         used_chunk_numbers = parsed.get("used_chunk_numbers", [])
#         reasoning_notes = parsed.get("reasoning_notes", {})

#         if answer_mode not in {"direct_answer", "scoped_answer", "partial_answer", "not_found"}:
#             answer_mode = "not_found"

#         if not isinstance(used_chunk_numbers, list):
#             used_chunk_numbers = []

#         if not isinstance(reasoning_notes, dict):
#             reasoning_notes = {}

#         if answer_mode == "not_found" or not answer:
#             answer = ABSTAIN_ANSWER
#             answer_mode = "not_found"

#         return {
#             "answer_mode": answer_mode,
#             "answer": answer,
#             "used_chunk_numbers": used_chunk_numbers,
#             "reasoning_notes": reasoning_notes,
#             "raw_output": raw_output
#         }

#     except Exception:
#         # If model output is malformed, fail safely
#         return {
#             "answer_mode": "not_found",
#             "answer": ABSTAIN_ANSWER,
#             "used_chunk_numbers": [],
#             "reasoning_notes": {
#                 "has_multiple_cases": False,
#                 "has_partial_support": False
#             },
#             "raw_output": raw_output
#         }
import json
import re
from openai import OpenAI

from app.core.config import settings
from app.llm.prompts import SYSTEM_PROMPT
from app.llm.groq_client import groq_client

ABSTAIN_ANSWER = "I could not find a reliable answer in the uploaded tenant documents."


def build_context(chunks: list[dict]) -> str:
    context_parts = []

    for idx, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"""[Chunk {idx}]
Title: {chunk.get("title", "")}
Doc Type: {chunk.get("doc_type", "")}
File: {chunk.get("file_name", "")}
Page: {chunk.get("page_number", "")}
Content:
{chunk.get("chunk_text", "")}
"""
        )

    return "\n\n".join(context_parts)


def strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def call_openai(system_prompt: str, user_prompt: str) -> str:
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )

    return response.choices[0].message.content.strip()


def call_groq(system_prompt: str, user_prompt: str) -> str:
    response = groq_client.chat.completions.create(
        model=settings.GROQ_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()

# def generate_grounded_answer(question: str, chunks: list[dict], allow_rescue: bool = True) -> dict:
#     """
#     Main answer generation.
#     Uses a second-pass rescue only when the first pass abstains.
#     """
#     primary_prompt = build_primary_user_prompt(question, chunks)
#     raw_output = call_llm(SYSTEM_PROMPT, primary_prompt)
#     parsed = parse_llm_json(raw_output)

#     if parsed["answer_mode"] != "not_found":
#         return parsed
#     if not allow_rescue:
#         return parsed
#     # Rescue pass:
#     # only if there is at least some meaningful chunk evidence in the input set
#     # (we don't have retrieval scores here, so the caller should already have filtered bad cases)
#     rescue_prompt = build_rescue_user_prompt(question, chunks)
#     rescue_raw_output = call_llm(SYSTEM_PROMPT, rescue_prompt)
#     rescue_parsed = parse_llm_json(rescue_raw_output)

#     # If rescue still says not_found, keep it
#     return rescue_parsed
def generate_grounded_answer(question: str, chunks: list[dict], allow_rescue: bool = True) -> dict:
    """
    Main answer generation.
    Uses a second-pass rescue only when the first pass abstains and allow_rescue=True.
    """
    primary_prompt = build_primary_user_prompt(question, chunks)
    raw_output = call_llm(SYSTEM_PROMPT, primary_prompt)
    parsed = parse_llm_json(raw_output)

    # If primary pass succeeded, mark rescue_used=False
    if parsed["answer_mode"] != "not_found":
        parsed["rescue_used"] = False
        return parsed

    # If rescue is not allowed, return primary abstention
    if not allow_rescue:
        parsed["rescue_used"] = False
        return parsed

    # Rescue pass
    rescue_prompt = build_rescue_user_prompt(question, chunks)
    rescue_raw_output = call_llm(SYSTEM_PROMPT, rescue_prompt)
    rescue_parsed = parse_llm_json(rescue_raw_output)
    rescue_parsed["rescue_used"] = True

    return rescue_parsed

def call_llm(system_prompt: str, user_prompt: str) -> str:
    provider = settings.ANSWER_LLM_PROVIDER.lower().strip()

    if provider == "openai":
        return call_openai(system_prompt, user_prompt)
    elif provider == "groq":
        return call_groq(system_prompt, user_prompt)
    else:
        raise ValueError(f"Unsupported ANSWER_LLM_PROVIDER: {settings.ANSWER_LLM_PROVIDER}")


def parse_llm_json(raw_output: str) -> dict:
    cleaned = strip_code_fences(raw_output)

    try:
        parsed = json.loads(cleaned)
    except Exception:
        return {
            "answer_mode": "not_found",
            "answer": ABSTAIN_ANSWER,
            "used_chunk_numbers": [],
            "reasoning_notes": {
                "has_multiple_cases": False,
                "has_partial_support": False
            },
            "raw_output": raw_output
        }

    answer_mode = str(parsed.get("answer_mode", "")).strip()
    answer = str(parsed.get("answer", "")).strip()
    used_chunk_numbers = parsed.get("used_chunk_numbers", [])
    reasoning_notes = parsed.get("reasoning_notes", {})

    if answer_mode not in {"direct_answer", "scoped_answer", "partial_answer", "not_found"}:
        answer_mode = "not_found"

    if not isinstance(used_chunk_numbers, list):
        used_chunk_numbers = []

    cleaned_chunk_numbers = []
    for item in used_chunk_numbers:
        if isinstance(item, int) and item >= 1:
            cleaned_chunk_numbers.append(item)
    used_chunk_numbers = cleaned_chunk_numbers

    if not isinstance(reasoning_notes, dict):
        reasoning_notes = {}

    if answer_mode == "not_found" or not answer:
        answer = ABSTAIN_ANSWER
        answer_mode = "not_found"

    return {
        "answer_mode": answer_mode,
        "answer": answer,
        "used_chunk_numbers": used_chunk_numbers,
        "reasoning_notes": reasoning_notes,
        "raw_output": raw_output
    }


def build_primary_user_prompt(question: str, chunks: list[dict]) -> str:
    context = build_context(chunks)

    return f"""
Question:
{question}

Context:
{context}
"""


def build_rescue_user_prompt(question: str, chunks: list[dict]) -> str:
    context = build_context(chunks)

    return f"""
The first pass may have been overly conservative.

Question:
{question}

Context:
{context}

Task:
- Re-read the chunks carefully.
- If the chunks support ANY grounded answer about the asked policy/process/list/FAQ/deduction/coverage topic, do NOT return not_found.
- Instead return either:
  - direct_answer if one clear answer is supported
  - scoped_answer if multiple supported cases / categories / process steps are present
  - partial_answer if only part of the answer is supported
- Only use not_found if the chunks truly do not contain usable evidence for the question.
- Preserve important policy terms from the question when supported by the chunks.
"""