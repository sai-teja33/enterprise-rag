import csv
import json
from pathlib import Path
from typing import Any

import requests


# =========================
# CONFIG
# =========================
BASE_URL = "http://127.0.0.1:8000"
ASK_ENDPOINT = f"{BASE_URL}/query/ask"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVAL_CASES_PATH = PROJECT_ROOT / "eval" / "eval_cases.json"
RESULTS_DIR = PROJECT_ROOT / "eval" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_JSON_PATH = RESULTS_DIR / "eval_results.json"
RESULTS_CSV_PATH = RESULTS_DIR / "eval_results.csv"
SUMMARY_JSON_PATH = RESULTS_DIR / "eval_summary.json"


# =========================
# DOC TYPE NORMALIZATION
# =========================
def normalize_doc_type(doc_type: str | None, title: str | None = None, file_name: str | None = None) -> str | None:
    """
    Normalize raw stored doc_type / title / filename into broad eval categories.
    """
    text = " ".join([
        doc_type or "",
        title or "",
        file_name or ""
    ]).lower()

    if any(x in text for x in ["leave"]):
        # if attendance is also explicitly present, we still allow leave/attendance overlap
        if "attendance" in text:
            return "attendance_policy"
        return "leave_policy"

    if any(x in text for x in ["attendance", "shift attendance"]):
        return "attendance_policy"

    if any(x in text for x in ["insurance", "medical", "health"]):
        return "insurance_policy"

    if any(x in text for x in ["travel", "reimbursement", "hotel", "expense"]):
        return "travel_policy"

    if any(x in text for x in ["conduct", "uniform"]):
        return "conduct_policy"

    if any(x in text for x in ["probation", "notice", "separation"]):
        return "notice_policy"

    if any(x in text for x in ["performance", "review"]):
        return "performance_policy"

    if any(x in text for x in ["work from home", "hybrid work", "wfh", "work policy"]):
        return "work_policy"

    if any(x in text for x in ["payroll", "deduction"]):
        return "payroll_policy"

    if any(x in text for x in ["grievance", "posh"]):
        return "grievance_policy"

    if any(x in text for x in ["security", "data handling", "information security"]):
        return "security_policy"

    if any(x in text for x in ["benefits", "wellness", "overtime", "holiday compensation"]):
        return "benefits_policy"

    if any(x in text for x in ["handbook"]):
        return "employee_handbook"

    return doc_type


# =========================
# EVAL HELPERS
# =========================
def load_eval_cases() -> list[dict]:
    with open(EVAL_CASES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def ask_question(tenant_id: str, question: str, top_k: int = 5) -> dict:
    payload = {
        "tenant_id": tenant_id,
        "question": question,
        "top_k": top_k
    }
    response = requests.post(ASK_ENDPOINT, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def extract_citation_doc_types(response_json: dict) -> list[str]:
    citations = response_json.get("used_citations", []) or []
    normalized = []

    for c in citations:
        doc_type = c.get("doc_type")
        title = c.get("title")
        file_name = c.get("file_name")
        normalized_type = normalize_doc_type(doc_type, title, file_name)
        if normalized_type:
            normalized.append(normalized_type)

    return normalized


def extract_citation_tenants(response_json: dict) -> list[str]:
    """
    Your current citations may or may not include tenant_id.
    If not present, this will return empty strings for those entries.
    """
    citations = response_json.get("used_citations", []) or []
    tenants = []

    for c in citations:
        tenant = c.get("tenant_id")
        if tenant:
            tenants.append(str(tenant))

    return tenants


def contains_expected_keywords(answer: str, expected_keywords: list[str]) -> bool:
    if not expected_keywords:
        return True

    answer_l = (answer or "").lower()
    return all(keyword.lower() in answer_l for keyword in expected_keywords)


def evaluate_case(case: dict, response_json: dict) -> dict:
    tenant_id = case["tenant_id"]
    answerable = case["answerable"]
    expected_doc_types = case.get("expected_doc_types", [])
    expected_keywords = case.get("expected_keywords", [])

    answer_mode = response_json.get("answer_mode")
    answer = response_json.get("answer", "") or ""
    used_citations = response_json.get("used_citations", []) or []

    citation_doc_types = extract_citation_doc_types(response_json)
    citation_tenants = extract_citation_tenants(response_json)

    # -------------------------
    # 1) answerability pass
    # -------------------------
    if answerable:
        answerability_pass = answer_mode != "not_found"
    else:
        answerability_pass = answer_mode == "not_found"

    # -------------------------
    # 2) doc type pass
    # -------------------------
    if not expected_doc_types:
        doc_type_pass = True
    else:
        doc_type_pass = any(doc_type in expected_doc_types for doc_type in citation_doc_types)

    # -------------------------
    # 3) keyword pass
    # only enforce for answerable cases that were not not_found
    # -------------------------
    if answerable and answer_mode != "not_found":
        keyword_pass = contains_expected_keywords(answer, expected_keywords)
    else:
        keyword_pass = True

    # -------------------------
    # 4) tenant isolation pass
    # If citations do not contain tenant_id, we mark as "not_checked"
    # rather than failing.
    # -------------------------
    if not citation_tenants:
        tenant_isolation_status = "not_checked"
        tenant_isolation_pass = True
    else:
        tenant_isolation_pass = all(t == tenant_id for t in citation_tenants)
        tenant_isolation_status = "pass" if tenant_isolation_pass else "fail"

    # -------------------------
    # 5) overall pass
    # For now:
    #   overall_pass = answerability AND doc_type AND keyword AND tenant isolation
    # -------------------------
    overall_pass = (
        answerability_pass
        and doc_type_pass
        and keyword_pass
        and tenant_isolation_pass
    )

    retrieval_debug = response_json.get("retrieval_debug", {}) or {}

    return {
        "id": case["id"],
        "tenant_id": tenant_id,
        "question": case["question"],
        "answerable": answerable,
        "expected_doc_types": expected_doc_types,
        "expected_keywords": expected_keywords,

        "answer_mode": answer_mode,
        "answer": answer,
        "used_citations_count": len(used_citations),
        "citation_doc_types": citation_doc_types,
        "citation_tenants": citation_tenants,

        "answerability_pass": answerability_pass,
        "doc_type_pass": doc_type_pass,
        "keyword_pass": keyword_pass,
        "tenant_isolation_status": tenant_isolation_status,
        "tenant_isolation_pass": tenant_isolation_pass,
        "overall_pass": overall_pass,

        "top_vector_score": retrieval_debug.get("top_vector_score"),
        "top_rerank_score": retrieval_debug.get("top_rerank_score"),
        "num_chunks": retrieval_debug.get("num_chunks"),
        "lexical_overlap": retrieval_debug.get("lexical_overlap"),
    }


def build_summary(results: list[dict]) -> dict:
    total = len(results)

    error_cases = [r for r in results if r.get("answer_mode") == "error"]
    valid_cases = [r for r in results if r.get("answer_mode") != "error"]

    answerability_pass = sum(1 for r in valid_cases if r["answerability_pass"])
    doc_type_pass = sum(1 for r in valid_cases if r["doc_type_pass"])
    keyword_pass = sum(1 for r in valid_cases if r["keyword_pass"])
    overall_pass = sum(1 for r in valid_cases if r["overall_pass"])

    tenant_checked = [r for r in valid_cases if r["tenant_isolation_status"] != "not_checked"]
    if tenant_checked:
        tenant_isolation_pass = sum(1 for r in tenant_checked if r["tenant_isolation_pass"])
        tenant_isolation_rate = round(tenant_isolation_pass / len(tenant_checked), 4)
    else:
        tenant_isolation_pass = None
        tenant_isolation_rate = None

    answerable_cases = [r for r in valid_cases if r["answerable"]]
    unanswerable_cases = [r for r in valid_cases if not r["answerable"]]

    answerable_correct = sum(1 for r in answerable_cases if r["answerability_pass"])
    unanswerable_correct = sum(1 for r in unanswerable_cases if r["answerability_pass"])

    return {
        "total_cases": total,
        "error_cases": len(error_cases),
        "valid_cases": len(valid_cases),

        "answerability_pass_count": answerability_pass,
        "answerability_pass_rate": round(answerability_pass / len(valid_cases), 4) if valid_cases else 0,

        "doc_type_pass_count": doc_type_pass,
        "doc_type_pass_rate": round(doc_type_pass / len(valid_cases), 4) if valid_cases else 0,

        "keyword_pass_count": keyword_pass,
        "keyword_pass_rate": round(keyword_pass / len(valid_cases), 4) if valid_cases else 0,

        "overall_pass_count": overall_pass,
        "overall_pass_rate": round(overall_pass / len(valid_cases), 4) if valid_cases else 0,

        "tenant_isolation_checked_cases": len(tenant_checked),
        "tenant_isolation_pass_count": tenant_isolation_pass,
        "tenant_isolation_pass_rate": tenant_isolation_rate,

        "answerable_cases": len(answerable_cases),
        "answerable_answerability_pass_count": answerable_correct,
        "answerable_answerability_pass_rate": round(answerable_correct / len(answerable_cases), 4) if answerable_cases else 0,

        "unanswerable_cases": len(unanswerable_cases),
        "unanswerable_answerability_pass_count": unanswerable_correct,
        "unanswerable_answerability_pass_rate": round(unanswerable_correct / len(unanswerable_cases), 4) if unanswerable_cases else 0
    }
 
def write_json(path: Path, data: Any):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_csv(path: Path, results: list[dict]):
    if not results:
        return

    fieldnames = [
        "id",
        "tenant_id",
        "question",
        "answerable",
        "answer_mode",
        "answer",
        "used_citations_count",
        "citation_doc_types",
        "citation_tenants",
        "answerability_pass",
        "doc_type_pass",
        "keyword_pass",
        "tenant_isolation_status",
        "tenant_isolation_pass",
        "overall_pass",
        "top_vector_score",
        "top_rerank_score",
        "num_chunks"
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in results:
            csv_row = row.copy()
            csv_row["citation_doc_types"] = ", ".join(csv_row.get("citation_doc_types", []))
            csv_row["citation_tenants"] = ", ".join(csv_row.get("citation_tenants", []))
            writer.writerow({k: csv_row.get(k) for k in fieldnames})


def main():
    cases = load_eval_cases()
    results = []

    print(f"Loaded {len(cases)} eval cases.")
    print(f"Calling API at: {ASK_ENDPOINT}")

    for idx, case in enumerate(cases, start=1):
        print(f"[{idx}/{len(cases)}] {case['id']} | tenant={case['tenant_id']} | q={case['question']}")

        try:
            response_json = ask_question(
                tenant_id=case["tenant_id"],
                question=case["question"],
                top_k=5
            )
            evaluated = evaluate_case(case, response_json)
        except Exception as e:
            evaluated = {
                "id": case["id"],
                "tenant_id": case["tenant_id"],
                "question": case["question"],
                "answerable": case["answerable"],
                "expected_doc_types": case.get("expected_doc_types", []),
                "expected_keywords": case.get("expected_keywords", []),

                "answer_mode": "error",
                "answer": "",
                "used_citations_count": 0,
                "citation_doc_types": [],
                "citation_tenants": [],

                "answerability_pass": False,
                "doc_type_pass": False,
                "keyword_pass": False,
                "tenant_isolation_status": "not_checked",
                "tenant_isolation_pass": True,
                "overall_pass": False,

                "top_vector_score": None,
                "top_rerank_score": None,
                "num_chunks": None,
                "lexical_overlap": None,
                "error": str(e)
            }

        results.append(evaluated)

    summary = build_summary(results)

    write_json(RESULTS_JSON_PATH, results)
    write_csv(RESULTS_CSV_PATH, results)
    write_json(SUMMARY_JSON_PATH, summary)

    print("\n=== EVAL SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"\nSaved results to:")
    print(f"- {RESULTS_JSON_PATH}")
    print(f"- {RESULTS_CSV_PATH}")
    print(f"- {SUMMARY_JSON_PATH}")


if __name__ == "__main__":
    main()