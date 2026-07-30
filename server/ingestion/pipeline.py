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

import tiktoken

encoding = tiktoken.encoding_for_model("text-embedding-3-small")


def process_document_into_chunks(document_id: str):
    doc = get_document_by_id(document_id)
    if doc is None:
        raise ValueError("Document not found")

    docs = load_document(
        doc["file_path"],
        base_metadata={
            "document_id": str(doc["_id"]),
            "title": doc["title"],
            "doc_type": doc["doc_type"],
            "file_name": doc["file_name"]
        }
    )
    print("\n" + "=" * 80)
    print("PDF LOADER DEBUG")
    print("=" * 80)
    print(f"TOTAL DOCUMENTS RETURNED: {len(docs)}")

    for i, d in enumerate(docs[:10]):

        print(f"\nDocument #{i+1}")

        print("Page:", d.metadata.get("page_number"))

        print("Block Count:", d.metadata.get("block_count"))

        print("Content Preview:")
        print(d.page_content[:250])

    print("=" * 80)

    if not docs:
        raise ValueError("No text could be extracted from document")

    chunking_strategy, chunked_records = chunk_loaded_documents(
        docs=docs,
        doc_type=doc.get("doc_type")
    )

    chunk_records = []

    for idx, chunk in enumerate(chunked_records):

        section_title = chunk.get("section_title") or "General"

        page_start = chunk.get("page_start")
        page_end = chunk.get("page_end")

        if page_start is None:
            page_text = "Unknown"
        elif page_start == page_end:
            page_text = str(page_start)
        else:
            page_text = f"{page_start}-{page_end}"

        embedding_text = (
            f"Document: {doc['title']}\n"
            f"Document Type: {doc['doc_type']}\n"
            f"Section: {section_title}\n"
            f"Pages: {page_text}\n\n"
            f"{chunk['chunk_text']}"
        )

        chunk_records.append({
            "document_id": str(doc["_id"]),
            "title": doc["title"],
            "doc_type": doc["doc_type"],
            "file_name": doc["file_name"],

            "page_start": page_start,
            "page_end": page_end,

            "section_title": section_title,
            "parent_section": chunk.get("parent_section"),
            "heading_level": chunk.get("heading_level"),
            "element_type": chunk.get("element_type"),
            "chunk_index": idx,

            "chunk_text": chunk["chunk_text"],
            "embedding_text": embedding_text,

            "chunk_size": len(chunk["chunk_text"]),
            "token_count": len(encoding.encode(chunk["chunk_text"])),

            "chunking_strategy": chunk["chunking_strategy"]
        })

    deleted_old_chunks = delete_chunks_by_document(str(doc["_id"]))

    saved_chunks = create_chunks(chunk_records)

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

    # Embed the enriched text if available
    texts = [
        chunk.get("embedding_text", chunk["chunk_text"])
        for chunk in chunks
    ]

    embeddings = embedder.embed_documents(texts)

    for chunk, embedding in zip(chunks, embeddings):
        update_chunk_embedding(chunk["_id"], embedding)

    return {
        "document_id": document_id,
        "embedded_chunks": len(chunks)
    }