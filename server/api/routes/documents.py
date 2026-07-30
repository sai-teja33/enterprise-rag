import os
import shutil
from pathlib import Path
from utils.pdf_utils import extract_preview_text
from classification.doc_classifier import classify_document

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.document import DocumentResponse

from db.repositories.document_repo import (
    create_document,
    get_all_documents,
    get_document_by_id
)
from db.repositories.chunk_repo import (
    get_chunks_by_document,
    count_chunks_by_document,
    count_embedded_chunks_by_document,
    delete_chunks_by_document
)

from ingestion.loaders.factory import load_document
from ingestion.pipeline import process_document_into_chunks,embed_document_chunks
from ingestion.batch_ingestion import bulk_ingest_folder

router = APIRouter(prefix="/documents", tags=["Documents"])

BASE_UPLOAD_DIR = Path("data/raw")


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...)
):
    allowed_extensions = {".pdf", ".docx"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")

    BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_path = BASE_UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    preview = extract_preview_text(str(file_path))

    doc_type = classify_document(
    file_name=file.filename,
    preview=preview)

    saved_doc = create_document(
    title=title,
    doc_type=doc_type,
    file_name=file.filename,
    file_path=str(file_path)
)

    return DocumentResponse(
        id=str(saved_doc["_id"]),
        
        title=saved_doc["title"],
        doc_type=saved_doc["doc_type"],
        file_name=saved_doc["file_name"],
        file_path=saved_doc["file_path"],
        uploaded_at=saved_doc["uploaded_at"]
    )


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents():


    docs = get_all_documents()

    return [
        DocumentResponse(
            id=str(d["_id"]),
            
            title=d["title"],
            doc_type=d["doc_type"],
            file_name=d["file_name"],
            file_path=d["file_path"],
            uploaded_at=d["uploaded_at"]
        )
        for d in docs
    ]


@router.get("/{document_id}/preview")
def preview_document_text(document_id: str):


    doc = get_document_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")


    try:
        docs = load_document(
            doc["file_path"],
            base_metadata={

                "title": doc["title"],
                "doc_type": doc["doc_type"],
                "document_id": str(doc["_id"]),
                "file_name": doc["file_name"]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")

    full_text = "\n\n".join(d.page_content for d in docs).strip()

    return {
        "document_id": str(doc["_id"]),
        "title": doc["title"],
        "doc_type": doc["doc_type"],
        "file_name": doc["file_name"],
        "num_langchain_docs": len(docs),
        "text_preview": full_text[:3000],
        "text_length": len(full_text)
    }


@router.post("/{document_id}/chunk")
def chunk_document(document_id: str):


    doc = get_document_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")



    try:
        result = process_document_into_chunks(document_id)
        return {
            "message": "Document chunked successfully",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunking failed: {str(e)}")


@router.get("/{document_id}/chunks")
def list_document_chunks(document_id: str):


    doc = get_document_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")



    chunks = get_chunks_by_document(document_id)

    return {
        "document_id": document_id,
        "total_chunks": len(chunks),
        "chunks": [
            {
                "id": str(chunk["_id"]),
                "chunk_index": chunk["chunk_index"],
                "page_number": chunk.get("page_number"),
                "section_title": chunk.get("section_title"),
                "chunking_strategy": chunk.get("chunking_strategy"),
                "chunk_size": chunk.get("chunk_size"),
                "chunk_preview": chunk["chunk_text"][:300]
            }
            for chunk in chunks
        ]
    }
@router.post("/{document_id}/embed")
def embed_chunks_for_document(document_id: str):


    doc = get_document_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")


    try:
        result = embed_document_chunks(document_id)
        return {
            "message": "Chunk embeddings generated successfully",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")
@router.post("/bulk-ingest")
def bulk_ingest_documents(
    reprocess_existing: bool = False
):


    try:
        result = bulk_ingest_folder(

            reprocess_existing=reprocess_existing
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk ingestion failed: {str(e)}")
@router.get("/status")
def get_document_status():


    docs = get_all_documents()

    results = []
    for doc in docs:
        document_id = str(doc["_id"])
        total_chunks = count_chunks_by_document(document_id)
        embedded_chunks = count_embedded_chunks_by_document(document_id)

        results.append({
            "document_id": document_id,
            "title": doc["title"],
            "doc_type": doc["doc_type"],
            "file_name": doc["file_name"],
            "uploaded_at": doc["uploaded_at"],
            "total_chunks": total_chunks,
            "embedded_chunks": embedded_chunks,
            "ready_for_query": total_chunks > 0 and embedded_chunks == total_chunks
        })

    return {

        "total_documents": len(results),
        "documents": results
    }
@router.post("/{document_id}/reprocess")
def reprocess_document(document_id: str):


    doc = get_document_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")



    try:
        # 1) delete existing chunks for this document
        deleted_chunks = delete_chunks_by_document(document_id)

        # 2) re-run chunking
        chunk_result = process_document_into_chunks(document_id)

        # 3) re-run embeddings
        embed_result = embed_document_chunks(document_id)

        # 4) final counts
        total_chunks = count_chunks_by_document(document_id)
        embedded_chunks = count_embedded_chunks_by_document(document_id)

        return {
            "message": "Document reprocessed successfully",
            "document_id": document_id,
            "title": doc["title"],
            "doc_type": doc["doc_type"],
            "deleted_old_chunks": deleted_chunks,
            "chunking": chunk_result,
            "embedding": embed_result,
            "final_status": {
                "total_chunks": total_chunks,
                "embedded_chunks": embedded_chunks,
                "ready_for_query": total_chunks > 0 and embedded_chunks == total_chunks
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")