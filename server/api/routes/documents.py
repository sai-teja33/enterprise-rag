import os
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.document import DocumentResponse

from db.repositories.document_repo import (
    create_document,
    get_documents_by_department,
    get_document_by_id
)
from db.repositories.chunk_repo import (
    get_chunks_by_document,
    count_chunks_by_document,
    count_embedded_chunks_by_document,
    delete_chunks_by_document
)
from db.mongo import departments_collection
from ingestion.loaders.factory import load_document
from ingestion.pipeline import process_document_into_chunks,embed_document_chunks
from ingestion.batch_ingestion import bulk_ingest_department_folder

router = APIRouter(prefix="/departments", tags=["Documents"])

BASE_UPLOAD_DIR = Path("data/raw")


@router.post("/{department_id}/documents/upload", response_model=DocumentResponse)
def upload_document(
    department_id: str,
    title: str = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...)
):
    department = departments_collection.find_one({"slug": department_id})
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")

    department_slug = department["slug"]

    allowed_extensions = {".pdf", ".docx"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")

    department_folder = BASE_UPLOAD_DIR / department_slug
    department_folder.mkdir(parents=True, exist_ok=True)

    file_path = department_folder / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    saved_doc = create_document(
        department_id=str(department["_id"]),
        title=title,
        doc_type=doc_type,
        file_name=file.filename,
        file_path=str(file_path)
    )

    return DocumentResponse(
        id=str(saved_doc["_id"]),
        department_id=saved_doc["department_id"],
        title=saved_doc["title"],
        doc_type=saved_doc["doc_type"],
        file_name=saved_doc["file_name"],
        file_path=saved_doc["file_path"],
        uploaded_at=saved_doc["uploaded_at"]
    )


@router.get("/{department_id}/documents", response_model=list[DocumentResponse])
def list_documents(department_id: str):
    department = departments_collection.find_one({"slug": department_id})
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")

    docs = get_documents_by_department(str(department["_id"]))

    return [
        DocumentResponse(
            id=str(d["_id"]),
            department_id=d["department_id"],
            title=d["title"],
            doc_type=d["doc_type"],
            file_name=d["file_name"],
            file_path=d["file_path"],
            uploaded_at=d["uploaded_at"]
        )
        for d in docs
    ]


@router.get("/{department_id}/documents/{document_id}/preview")
def preview_document_text(department_id: str, document_id: str):
    department = departments_collection.find_one({"slug": department_id})
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")

    doc = get_document_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc["department_id"] != str(department["_id"]):
        raise HTTPException(status_code=403, detail="This document does not belong to the given department")

    try:
        docs = load_document(
            doc["file_path"],
            base_metadata={
                "department_id": doc["department_id"],
                "title": doc["title"],
                "doc_type": doc["doc_type"],
                "document_id": str(doc["_id"])
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


@router.post("/{department_id}/documents/{document_id}/chunk")
def chunk_document(department_id: str, document_id: str):
    department = departments_collection.find_one({"slug": department_id})
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")

    doc = get_document_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc["department_id"] != str(department["_id"]):
        raise HTTPException(status_code=403, detail="This document does not belong to the given department")

    try:
        result = process_document_into_chunks(document_id)
        return {
            "message": "Document chunked successfully",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunking failed: {str(e)}")


@router.get("/{department_id}/documents/{document_id}/chunks")
def list_document_chunks(department_id: str, document_id: str):
    department = departments_collection.find_one({"slug": department_id})
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")

    doc = get_document_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc["department_id"] != str(department["_id"]):
        raise HTTPException(status_code=403, detail="This document does not belong to the given department")

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
@router.post("/{department_id}/documents/{document_id}/embed")
def embed_chunks_for_document(department_id: str, document_id: str):
    department = departments_collection.find_one({"slug": department_id})
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")

    doc = get_document_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc["department_id"] != str(department["_id"]):
        raise HTTPException(status_code=403, detail="This document does not belong to the given department")

    try:
        result = embed_document_chunks(document_id)
        return {
            "message": "Chunk embeddings generated successfully",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")
@router.post("/{department_id}/documents/bulk-ingest")
def bulk_ingest_documents(
    department_id: str,
    reprocess_existing: bool = False
):
    department = departments_collection.find_one({"slug": department_id})
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")

    try:
        result = bulk_ingest_department_folder(
            department_slug=department_id,
            reprocess_existing=reprocess_existing
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk ingestion failed: {str(e)}")
@router.get("/{department_id}/documents/status")
def get_department_document_status(department_id: str):
    department = departments_collection.find_one({"slug": department_id})
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")

    docs = get_documents_by_department(str(department["_id"]))

    results = []
    for doc in docs:
        document_id = str(doc["_id"])
        total_chunks = count_chunks_by_document(document_id)
        embedded_chunks = count_embedded_chunks_by_document(document_id)

        results.append({
            "document_id": document_id,
            "department_id": department["slug"],
            "title": doc["title"],
            "doc_type": doc["doc_type"],
            "file_name": doc["file_name"],
            "uploaded_at": doc["uploaded_at"],
            "total_chunks": total_chunks,
            "embedded_chunks": embedded_chunks,
            "ready_for_query": total_chunks > 0 and embedded_chunks == total_chunks
        })

    return {
        "department_id": department["slug"],
        "total_documents": len(results),
        "documents": results
    }
@router.post("/{department_id}/documents/{document_id}/reprocess")
def reprocess_document(department_id: str, document_id: str):
    department = departments_collection.find_one({"slug": department_id})
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")

    doc = get_document_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc["department_id"] != str(department["_id"]):
        raise HTTPException(
            status_code=403,
            detail="This document does not belong to the given department"
        )

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
            "department_id": department["slug"],
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