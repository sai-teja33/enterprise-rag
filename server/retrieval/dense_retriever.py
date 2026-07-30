from db.mongo import chunks_collection
from ingestion.embeddings.embedder import embedder

VECTOR_INDEX_NAME = "chunk_vector_index"


def retrieve_similar_chunks(
    question: str,
    top_k: int = 5,
    doc_type: str | None = None
):
    query_embedding = embedder.embed_query(question)

    vector_search = {
        "index": VECTOR_INDEX_NAME,
        "path": "embedding",
        "queryVector": query_embedding,
        "numCandidates": 50,
        "limit": top_k,
    }

    if doc_type:
        vector_search["filter"] = {
            "equals": {
                "path": "doc_type",
                "value": doc_type
            }
        }

    pipeline = [
        {
            "$vectorSearch": vector_search
        },
        {
            "$project": {
                "_id": 1,
                "document_id": 1,
                "title": 1,
                "doc_type": 1,
                "file_name": 1,
                "page_start": 1,
                "page_end": 1,
                "page_number": 1,
                "section_title": 1,
                "parent_section": 1,
                "heading_level": 1,
                "element_type": 1,
                "chunk_index": 1,
                "chunk_text": 1,
                "chunk_size": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    return list(chunks_collection.aggregate(pipeline))