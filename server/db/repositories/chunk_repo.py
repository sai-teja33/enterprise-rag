from app.db.mongo import chunks_collection


def create_chunks(chunk_docs: list[dict]):
    if not chunk_docs:
        return []

    result = chunks_collection.insert_many(chunk_docs)

    inserted = []
    for chunk_doc, inserted_id in zip(chunk_docs, result.inserted_ids):
        chunk_doc["_id"] = inserted_id
        inserted.append(chunk_doc)

    return inserted


def delete_chunks_by_document(document_id: str):
    result = chunks_collection.delete_many({"document_id": document_id})
    return result.deleted_count

def count_chunks_by_document(document_id: str) -> int:
    return chunks_collection.count_documents({"document_id": document_id})


def count_embedded_chunks_by_document(document_id: str) -> int:
    return chunks_collection.count_documents({
        "document_id": document_id,
        "embedding": {"$exists": True, "$ne": None}
    })


def get_chunks_by_document(document_id: str):
    return list(
        chunks_collection.find({"document_id": document_id}).sort("chunk_index", 1)
    )


def get_unembedded_chunks_by_document(document_id: str):
    return list(
        chunks_collection.find({
            "document_id": document_id,
            "embedding": {"$exists": False}
        }).sort("chunk_index", 1)
    )


def update_chunk_embedding(chunk_id, embedding: list[float]):
    chunks_collection.update_one(
        {"_id": chunk_id},
        {"$set": {"embedding": embedding}}
    )