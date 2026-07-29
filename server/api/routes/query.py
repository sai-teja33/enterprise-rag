from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from db.mongo import departments_collection
from retrieval.hybrid_retriever import retrieve_hybrid_chunks
from retrieval.relevance_guard import lexical_overlap_score
from llm.answer_generator import generate_grounded_answer
from router.department_router import route_department
from core.config import settings
router = APIRouter(prefix="/query", tags=["Query"])


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=10)
    debug: bool = Field(default=False, description="Return retrieval/debug metadata")


MIN_VECTOR_SCORE_THRESHOLD = settings.MIN_VECTOR_SCORE
ABSTAIN_ANSWER = "I could not find a reliable answer in the uploaded department documents."


def build_citation(chunk_num: int, chunk: dict, department_slug: str) -> dict:
    """
    Standardize citation payload so all citations carry department information.
    """
    return {
        "chunk_number": chunk_num,
        "chunk_id": str(chunk["_id"]),
        "department": department_slug,
        "document_id": chunk["document_id"],
        "title": chunk.get("title"),
        "doc_type": chunk.get("doc_type"),
        "file_name": chunk.get("file_name"),
        "page_number": chunk.get("page_number"),
        "chunk_index": chunk.get("chunk_index"),
        "retrieval_sources": chunk.get("retrieval_sources", []),
        "vector_score": chunk.get("vector_score"),
        "text_score": chunk.get("text_score"),
        "rerank_score": chunk.get("rerank_score")
    }


def build_debug_chunk(chunk: dict) -> dict:
    return {
        "chunk_id": str(chunk["_id"]),
        "document_id": chunk.get("document_id"),
        "title": chunk.get("title"),
        "doc_type": chunk.get("doc_type"),
        "file_name": chunk.get("file_name"),
        "page_number": chunk.get("page_number"),
        "chunk_index": chunk.get("chunk_index"),
        "retrieval_sources": chunk.get("retrieval_sources", []),
        "vector_score": chunk.get("vector_score"),
        "text_score": chunk.get("text_score"),
        "rerank_score": chunk.get("rerank_score"),
        "vector_rank": chunk.get("vector_rank"),
        "text_rank": chunk.get("text_rank"),
        "chunk_preview": chunk.get("chunk_text", "")[:500]
    }


@router.post("/search")
def hybrid_search(payload: QueryRequest):
    routing = route_department(payload.question)

    # department_slug = routing["department"]
    department_slug = "hr"

    routing = {
        "department": "hr",
        "method": "fixed",
        "confidence": 1.0}
 
    if department_slug == "unknown":
        raise HTTPException(
            status_code=400,
            detail="Unable to determine the appropriate department for this question.")
    
    
    department = departments_collection.find_one(
    {"slug": department_slug})
    if department is None:
        raise HTTPException(
        status_code=404,
        detail="Department not found")
    

    department_db_id = str(department["_id"])
 
    try:
        retrieval = retrieve_hybrid_chunks(
            department_id=department_db_id,
            question=payload.question,
            top_k=payload.top_k,
            rerank_top_k=payload.top_k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hybrid retrieval failed: {str(e)}")

    chunks = retrieval["merged_chunks"]

    return {
        "department": department_slug,
        "routing": routing,
        "question": payload.question,
        "total_results": len(chunks),
        "results": [
            {
                "chunk_id": str(chunk["_id"]),
                "department": department_slug,
                "document_id": chunk["document_id"],
                "title": chunk.get("title"),
                "doc_type": chunk.get("doc_type"),
                "file_name": chunk.get("file_name"),
                "page_number": chunk.get("page_number"),
                "chunk_index": chunk.get("chunk_index"),
                "chunk_preview": chunk.get("chunk_text", "")[:500],
                "retrieval_sources": chunk.get("retrieval_sources", []),
                "vector_score": chunk.get("vector_score"),
                "text_score": chunk.get("text_score"),
                "rerank_score": chunk.get("rerank_score"),
                "vector_rank": chunk.get("vector_rank"),
                "text_rank": chunk.get("text_rank")
            }
            for chunk in chunks
        ]
    }


@router.post("/ask")
def ask_question(payload: QueryRequest):
    routing = route_department(payload.question)

    # department_slug = routing["department"]
    department_slug = "hr"

    routing = {
        "department": "hr",
        "method": "fixed",
        "confidence": 1.0}

    if department_slug == "unknown":
        raise HTTPException(
              status_code=400,
              detail="Unable to determine the appropriate department for this question."
    )
    department = departments_collection.find_one(
    {"slug": department_slug})


    if department is None:
        raise HTTPException(
        status_code=404,
        detail="Department not found")
        

    department_db_id = str(department["_id"])

    try:
        retrieval = retrieve_hybrid_chunks(
            department_id=department_db_id,
            question=payload.question,
            top_k=payload.top_k,
            rerank_top_k=payload.top_k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hybrid retrieval failed: {str(e)}")

    chunks = retrieval["merged_chunks"]

    # Case 1: no chunks found
    if not chunks:
        response = {
            "department": department_slug,
            "routing": routing,
            "question": payload.question,
            "answer_mode": "not_found",
            "answer": ABSTAIN_ANSWER,
            "reasoning_notes": {
                "has_multiple_cases": False,
                "has_partial_support": False
            },
            "used_citations": [],
            "retrieval_debug": {
                "top_vector_score": None,
                "top_rerank_score": None,
                "num_chunks": 0,
                "lexical_overlap": {
                    "question_tokens": [],
                    "matched_tokens": [],
                    "coverage_ratio": 0.0
                }
            }
        }

        if payload.debug:
            response["debug_info"] = {
                "rescue_used": False,
                "retrieval": {
                    "top_vector_score": None,
                    "top_rerank_score": None,
                    "num_chunks": 0,
                    "lexical_overlap": {
                        "question_tokens": [],
                        "matched_tokens": [],
                        "coverage_ratio": 0.0
                    },
                    "retrieved_chunks": []
                }
            }

        return response

    overlap = lexical_overlap_score(payload.question, chunks)

    vector_scores = [c.get("vector_score") for c in chunks if c.get("vector_score") is not None]
    top_vector_score = max(vector_scores) if vector_scores else 0.0

    rerank_scores = [c.get("rerank_score") for c in chunks if c.get("rerank_score") is not None]
    top_rerank_score = max(rerank_scores) if rerank_scores else None

    debug_info = {
        "rescue_used": False,
        "retrieval": {
            "top_vector_score": top_vector_score,
            "top_rerank_score": top_rerank_score,
            "num_chunks": len(chunks),
            "lexical_overlap": overlap,
            "retrieved_chunks": [build_debug_chunk(chunk) for chunk in chunks]
        }
    }

    # Guardrail 1: weak vector evidence AND weak lexical overlap
    if top_vector_score < MIN_VECTOR_SCORE_THRESHOLD and overlap["coverage_ratio"] < 0.34:
        response = {
            "department": department_slug,
            "routing": routing,
            "question": payload.question,
            "answer_mode": "not_found",
            "answer": ABSTAIN_ANSWER,
            "reasoning_notes": {
                "has_multiple_cases": False,
                "has_partial_support": False
            },
            "used_citations": [],
            "retrieval_debug": {
                "top_vector_score": top_vector_score,
                "top_rerank_score": top_rerank_score,
                "num_chunks": len(chunks),
                "lexical_overlap": overlap
            }
        }

        if payload.debug:
            response["debug_info"] = debug_info

        return response

    # Guardrail 2: lexical overlap is absent
    if overlap["coverage_ratio"] == 0:
        response = {
            "department": department_slug,
            "routing": routing,
            "question": payload.question,
            "answer_mode": "not_found",
            "answer": ABSTAIN_ANSWER,
            "reasoning_notes": {
                "has_multiple_cases": False,
                "has_partial_support": False
            },
            "used_citations": [],
            "retrieval_debug": {
                "top_vector_score": top_vector_score,
                "top_rerank_score": top_rerank_score,
                "num_chunks": len(chunks),
                "lexical_overlap": overlap
            }
        }

        if payload.debug:
            response["debug_info"] = debug_info

        return response

    try:
        allow_rescue = (
            top_vector_score >= 0.80
            and (
                (top_rerank_score is not None and top_rerank_score >= 1.0)
                or overlap["coverage_ratio"] >= 0.60
            )
        )

        llm_result = generate_grounded_answer(
            payload.question,
            chunks,
            allow_rescue=allow_rescue
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {str(e)}")

    answer_mode = llm_result.get("answer_mode", "not_found")
    answer = llm_result.get("answer", ABSTAIN_ANSWER).strip()
    used_chunk_numbers = llm_result.get("used_chunk_numbers", [])
    reasoning_notes = llm_result.get("reasoning_notes", {})
    rescue_used = llm_result.get("rescue_used", False)

    debug_info["rescue_used"] = rescue_used

    if not answer:
        answer = ABSTAIN_ANSWER
        answer_mode = "not_found"

    # If model abstains, don't return citations
    if answer_mode == "not_found" or answer == ABSTAIN_ANSWER:
        response = {
            "department": department_slug,
            "routing": routing,
            "question": payload.question,
            "answer_mode": "not_found",
            "answer": ABSTAIN_ANSWER,
            "reasoning_notes": reasoning_notes or {
                "has_multiple_cases": False,
                "has_partial_support": False
            },
            "used_citations": [],
            "retrieval_debug": {
                "top_vector_score": top_vector_score,
                "top_rerank_score": top_rerank_score,
                "num_chunks": len(chunks),
                "lexical_overlap": overlap
            }
        }

        if payload.debug:
            response["debug_info"] = debug_info

        return response

    used_citations = []
    for chunk_num in used_chunk_numbers:
        if isinstance(chunk_num, int) and 1 <= chunk_num <= len(chunks):
            chunk = chunks[chunk_num - 1]
            used_citations.append(build_citation(chunk_num, chunk, department_slug))

    # fallback only for non-abstained answers
    if not used_citations:
        for idx, chunk in enumerate(chunks[:2], start=1):
            used_citations.append(build_citation(idx, chunk, department_slug))

    response = {
        "department": department_slug,
        "routing": routing,
        "question": payload.question,
        "answer_mode": answer_mode,
        "answer": answer,
        "reasoning_notes": reasoning_notes,
        "used_citations": used_citations,
        "retrieval_debug": {
            "top_vector_score": top_vector_score,
            "top_rerank_score": top_rerank_score,
            "num_chunks": len(chunks),
            "lexical_overlap": overlap
        }
    }

    if payload.debug:
        response["debug_info"] = debug_info

    return response