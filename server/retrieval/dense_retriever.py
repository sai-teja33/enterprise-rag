from app.db.mongo import chunks_collection
from app.ingestion.embeddings.embedder import embedder

VECTOR_INDEX_NAME = "chunk_vector_index"


def retrieve_similar_chunks(
    tenant_id: str,
    question: str,
    top_k: int = 5
):
    query_embedding = embedder.embed_query(question)

    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_INDEX_NAME,
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 50,
                "limit": top_k,
                "filter": {
                    "tenant_id": tenant_id
                }
            }
        },
        {
            "$project": {
                "_id": 1,
                "tenant_id": 1,
                "document_id": 1,
                "title": 1,
                "doc_type": 1,
                "file_name": 1,
                "page_number": 1,
                "chunk_index": 1,
                "chunk_text": 1,
                "chunk_size": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    results = list(chunks_collection.aggregate(pipeline))
    return results