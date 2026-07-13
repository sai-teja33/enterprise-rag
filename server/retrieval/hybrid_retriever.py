from retrieval.dense_retriever import retrieve_similar_chunks
from retrieval.text_retriever import retrieve_text_chunks
from retrieval.reranker import reranker


def merge_hybrid_results(
    vector_chunks: list[dict],
    text_chunks: list[dict]
) -> list[dict]:
    """
    Merge vector + text results into a deduplicated candidate pool.
    We do NOT do final ranking here anymore.
    Final ranking will be done by the reranker.
    """
    merged = {}

    # Add vector results
    for rank, chunk in enumerate(vector_chunks, start=1):
        chunk_id = str(chunk["_id"])
        merged[chunk_id] = {
            **chunk,
            "retrieval_sources": ["vector"],
            "vector_score": chunk.get("score"),
            "text_score": None,
            "vector_rank": rank,
            "text_rank": None
        }

    # Merge text results
    for rank, chunk in enumerate(text_chunks, start=1):
        chunk_id = str(chunk["_id"])

        if chunk_id in merged:
            merged[chunk_id]["retrieval_sources"].append("text")
            merged[chunk_id]["text_score"] = chunk.get("score")
            merged[chunk_id]["text_rank"] = rank
        else:
            merged[chunk_id] = {
                **chunk,
                "retrieval_sources": ["text"],
                "vector_score": None,
                "text_score": chunk.get("score"),
                "vector_rank": None,
                "text_rank": rank
            }

    return list(merged.values())


def retrieve_hybrid_chunks(
    tenant_id: str,
    question: str,
    top_k: int = 5,
    vector_k: int = 8,
    text_k: int = 8,
    rerank_top_k: int = 5
):
    vector_chunks = retrieve_similar_chunks(
        tenant_id=tenant_id,
        question=question,
        top_k=vector_k
    )

    text_chunks = retrieve_text_chunks(
        tenant_id=tenant_id,
        question=question,
        top_k=text_k
    )

    merged_candidates = merge_hybrid_results(
        vector_chunks=vector_chunks,
        text_chunks=text_chunks
    )

    reranked_chunks = reranker.rerank(
        question=question,
        chunks=merged_candidates,
        top_k=rerank_top_k
    )

    return {
        "merged_chunks": reranked_chunks,          # final top reranked chunks
        "candidate_chunks": merged_candidates,     # pre-rerank candidate pool
        "vector_chunks": vector_chunks,
        "text_chunks": text_chunks
    }