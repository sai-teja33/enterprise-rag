from db.repositories.document_repo import (
    get_document_by_id,
    update_document_chunking_info
)
from db.repositories.chunk_repo import (
    create_chunks,
    delete_chunks_by_document,
    get_unembedded_chunks_by_document,
    update_chunk_embedding
)
from ingestion.loaders.factory import load_document
from ingestion.embeddings.embedder import embedder
from chunking.chunker import chunk_loaded_documents


def process_document_into_chunks(document_id: str):
    doc = get_document_by_id(document_id)
    if doc is None:
        raise ValueError("Document not found")

    docs = load_document(
        doc["file_path"],
        base_metadata={
            "department_id": doc["department_id"],
            "document_id": str(doc["_id"]),
            "title": doc["title"],
            "doc_type": doc["doc_type"],
            "file_name": doc["file_name"]
        }
    )

    if not docs:
        raise ValueError("No text could be extracted from document")

    # Step 13: choose chunking strategy based on doc_type and chunk accordingly
    chunking_strategy, chunked_records = chunk_loaded_documents(
        docs=docs,
        doc_type=doc.get("doc_type")
    )

    chunk_records = []
    for idx, chunk in enumerate(chunked_records):
        chunk_records.append({
            "department_id": doc["department_id"],
            "document_id": str(doc["_id"]),
            "title": doc["title"],
            "doc_type": doc["doc_type"],
            "file_name": doc["file_name"],

            "page_number": chunk.get("page_number"),
            "section_title": chunk.get("section_title"),

            "chunk_index": idx,
            "chunk_text": chunk["chunk_text"],
            "chunk_size": len(chunk["chunk_text"]),
            "chunking_strategy": chunk["chunking_strategy"]
        })

    # IMPORTANT: replace old chunks for this document
    deleted_old_chunks = delete_chunks_by_document(str(doc["_id"]))

    saved_chunks = create_chunks(chunk_records)

    # update document metadata with chunking info
    update_document_chunking_info(
        document_id=str(doc["_id"]),
        chunking_strategy=chunking_strategy,
        chunk_count=len(saved_chunks)
    )

    return {
        "document_id": str(doc["_id"]),
        "title": doc["title"],
        "chunking_strategy": chunking_strategy,
        "deleted_old_chunks": deleted_old_chunks,
        "total_source_docs": len(docs),
        "total_chunks": len(saved_chunks)
    }


def embed_document_chunks(document_id: str):
    chunks = get_unembedded_chunks_by_document(document_id)
    if not chunks:
        return {
            "document_id": document_id,
            "embedded_chunks": 0,
            "message": "No unembedded chunks found"
        }

    texts = [chunk["chunk_text"] for chunk in chunks]
    embeddings = embedder.embed_documents(texts)

    for chunk, embedding in zip(chunks, embeddings):
        update_chunk_embedding(chunk["_id"], embedding)

    return {
        "document_id": document_id,
        "embedded_chunks": len(chunks)
    }