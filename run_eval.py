#!/usr/bin/env python3
"""
RAG evaluation harness for the Enterprise HR RAG system.

Usage:
    export OPENAI_API_KEY=sk-...
    python run_eval.py --api-url http://localhost:8000/query/ask --dataset eval_dataset.json --output results.csv

What it does:
  1. Sends every question in eval_dataset.json to your /query/ask endpoint.
  2. Grades each answer against a human-written gold answer using an LLM judge (GPT-4o-mini by default).
  3. Checks whether the correct source document was actually retrieved (citation/retrieval accuracy).
  4. Checks abstention behaviour on unanswerable ("adversarial") questions -- a good enterprise RAG
     system should say "I don't know" rather than hallucinate when the docs don't cover something.
  5. Prints an accuracy report and writes a row-by-row CSV + summary JSON you can share with your manager.
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import requests

try:
    from openai import OpenAI
except ImportError:
    print("Missing dependency. Run: pip install openai requests")
    sys.exit(1)


JUDGE_SYSTEM_PROMPT = """You are grading answers from an HR policy question-answering system.
You will be given a QUESTION, a GOLD (reference) ANSWER written by a human from the source policy document,
and the SYSTEM ANSWER produced by the RAG system being evaluated.

Grade the SYSTEM ANSWER as one of:
- "CORRECT": the system answer contains all the key facts/numbers/conditions from the gold answer, with no contradictions. Wording can differ.
- "PARTIAL": the system answer is directionally right but missing an important fact/number/condition from the gold answer, OR includes an extra unsupported claim.
- "INCORRECT": the system answer contradicts the gold answer, states wrong numbers/conditions, or fails to actually answer the question.

Respond ONLY with strict JSON: {"verdict": "CORRECT|PARTIAL|INCORRECT", "reason": "one sentence"}
"""


def grade_with_judge(client, model, question, gold_answer, system_answer):
    user_prompt = f"QUESTION: {question}\n\nGOLD ANSWER: {gold_answer}\n\nSYSTEM ANSWER: {system_answer}"
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        verdict = str(data.get("verdict", "INCORRECT")).upper()
        if verdict not in ("CORRECT", "PARTIAL", "INCORRECT"):
            verdict = "INCORRECT"
        return verdict, data.get("reason", "")
    except Exception as e:
        return "JUDGE_ERROR", str(e)


def call_rag_api(api_url, question, top_k=5, timeout=60):
    payload = {"question": question, "top_k": top_k, "debug": True}
    t0 = time.time()
    try:
        r = requests.post(api_url, json=payload, timeout=timeout)
        latency = time.time() - t0
        r.raise_for_status()
        return r.json(), latency, None
    except Exception as e:
        return None, time.time() - t0, str(e)


def extract_cited_files(response_json):
    files = set()
    for c in response_json.get("used_citations", []) or []:
        fn = c.get("file_name")
        if fn:
            files.add(fn)
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-url", default="http://localhost:8000/query/ask",
                     help="Your RAG API's /query/ask endpoint")
    ap.add_argument("--dataset", default="eval_dataset.json")
    ap.add_argument("--output", default="results.csv")
    ap.add_argument("--summary", default="summary.json")
    ap.add_argument("--judge-model", default="gpt-4o-mini")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--sleep", type=float, default=0.3, help="delay between requests (seconds)")
    args = ap.parse_args()

    dataset = json.loads(Path(args.dataset).read_text())
    client = OpenAI()  # reads OPENAI_API_KEY from env

    rows = []
    for i, item in enumerate(dataset, 1):
        qid = item["id"]
        question = item["question"]
        category = item["category"]
        gold = item["expected_answer"]
        expected_file = item.get("source_file")

        print(f"[{i}/{len(dataset)}] {qid}: {question[:70]}...")

        resp_json, latency, err = call_rag_api(args.api_url, question, args.top_k)

        row = {
            "id": qid,
            "category": category,
            "question": question,
            "expected_answer": gold,
            "expected_source_file": expected_file or "",
            "latency_sec": round(latency, 2),
        }

        if err:
            row.update({
                "system_answer": "",
                "answer_mode": "error",
                "verdict": "ERROR",
                "judge_reason": err,
                "retrieval_hit": "",
                "cited_files": "",
            })
            rows.append(row)
            print(f"    -> ERROR calling API: {err}")
            continue

        answer_mode = resp_json.get("answer_mode", "")
        system_answer = resp_json.get("answer", "")
        cited_files = extract_cited_files(resp_json)

        row["system_answer"] = system_answer
        row["answer_mode"] = answer_mode
        row["cited_files"] = ";".join(sorted(cited_files))

        if category == "adversarial":
            # Correct behaviour on an unanswerable question is to abstain.
            if answer_mode == "not_found":
                row["verdict"] = "CORRECT_ABSTAIN"
                row["judge_reason"] = "Correctly abstained on an unanswerable question."
            else:
                row["verdict"] = "HALLUCINATED"
                row["judge_reason"] = "Should have abstained but produced an answer."
            row["retrieval_hit"] = ""
        else:
            if answer_mode == "not_found":
                row["verdict"] = "INCORRECT"
                row["judge_reason"] = "System abstained on an answerable question (false negative)."
            else:
                verdict, reason = grade_with_judge(client, args.judge_model, question, gold, system_answer)
                row["verdict"] = verdict
                row["judge_reason"] = reason
            row["retrieval_hit"] = bool(expected_file and expected_file in cited_files)

        print(f"    -> {row['verdict']}")
        rows.append(row)
        time.sleep(args.sleep)

    # ---- write CSV ----
    fieldnames = ["id", "category", "question", "expected_answer", "expected_source_file",
                  "system_answer", "answer_mode", "verdict", "judge_reason",
                  "retrieval_hit", "cited_files", "latency_sec"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # ---- aggregate metrics ----
    answerable = [r for r in rows if r["category"] != "adversarial"]
    adversarial = [r for r in rows if r["category"] == "adversarial"]

    n_answerable = len(answerable)
    n_correct = sum(1 for r in answerable if r["verdict"] == "CORRECT")
    n_partial = sum(1 for r in answerable if r["verdict"] == "PARTIAL")
    n_incorrect = sum(1 for r in answerable if r["verdict"] == "INCORRECT")
    n_error = sum(1 for r in answerable if r["verdict"] in ("ERROR", "JUDGE_ERROR"))

    accuracy_strict = n_correct / n_answerable if n_answerable else 0
    accuracy_lenient = (n_correct + 0.5 * n_partial) / n_answerable if n_answerable else 0

    n_retrieval_eval = sum(1 for r in answerable if r["expected_source_file"])
    n_retrieval_hits = sum(1 for r in answerable if r["retrieval_hit"] is True)
    retrieval_hit_rate = n_retrieval_hits / n_retrieval_eval if n_retrieval_eval else 0

    n_adv = len(adversarial)
    n_adv_correct = sum(1 for r in adversarial if r["verdict"] == "CORRECT_ABSTAIN")
    abstention_accuracy = n_adv_correct / n_adv if n_adv else 0

    avg_latency = sum(r["latency_sec"] for r in rows) / len(rows) if rows else 0

    summary = {
        "total_questions": len(rows),
        "answerable_questions": n_answerable,
        "adversarial_questions": n_adv,
        "answer_accuracy_strict_pct": round(accuracy_strict * 100, 1),
        "answer_accuracy_lenient_pct": round(accuracy_lenient * 100, 1),
        "breakdown": {
            "correct": n_correct,
            "partial": n_partial,
            "incorrect": n_incorrect,
            "error": n_error,
        },
        "retrieval_hit_rate_pct": round(retrieval_hit_rate * 100, 1),
        "abstention_accuracy_pct": round(abstention_accuracy * 100, 1),
        "avg_latency_sec": round(avg_latency, 2),
        "by_category": {},
    }

    categories = sorted(set(r["category"] for r in rows))
    for cat in categories:
        cat_rows = [r for r in rows if r["category"] == cat]
        cat_correct = sum(1 for r in cat_rows if r["verdict"] in ("CORRECT", "CORRECT_ABSTAIN"))
        summary["by_category"][cat] = {
            "count": len(cat_rows),
            "correct": cat_correct,
            "accuracy_pct": round(100 * cat_correct / len(cat_rows), 1) if cat_rows else 0,
        }

    Path(args.summary).write_text(json.dumps(summary, indent=2))

    print("\n" + "=" * 60)
    print("RAG EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total questions evaluated:       {summary['total_questions']}")
    print(f"  Answerable questions:          {n_answerable}")
    print(f"  Adversarial (should abstain):  {n_adv}")
    print()
    print(f"Answer accuracy (strict, CORRECT only):   {summary['answer_accuracy_strict_pct']}%")
    print(f"Answer accuracy (lenient, +0.5*PARTIAL):  {summary['answer_accuracy_lenient_pct']}%")
    print(f"  Correct:   {n_correct}")
    print(f"  Partial:   {n_partial}")
    print(f"  Incorrect: {n_incorrect}")
    print(f"  Errors:    {n_error}")
    print()
    print(f"Retrieval hit rate (correct source doc cited): {summary['retrieval_hit_rate_pct']}%")
    print(f"Abstention accuracy (correctly said 'not found' on unanswerable Qs): {summary['abstention_accuracy_pct']}%")
    print(f"Average response latency: {summary['avg_latency_sec']}s")
    print()
    print("By category:")
    for cat, stats in summary["by_category"].items():
        print(f"  {cat:14s}: {stats['correct']}/{stats['count']} correct ({stats['accuracy_pct']}%)")
    print()
    print(f"Full row-by-row results written to: {args.output}")
    print(f"Summary JSON written to: {args.summary}")


if __name__ == "__main__":
    main()
