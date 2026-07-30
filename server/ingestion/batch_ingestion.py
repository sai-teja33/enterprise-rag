from pathlib import Path
from typing import Optional
from utils.pdf_utils import extract_preview_text
from classification.doc_classifier import classify_document

from db.repositories.document_repo import (
    create_document,
    get_document_by_file_name,
    update_document_file_metadata
)
from ingestion.pipeline import process_document_into_chunks, embed_document_chunks


ALLOWED_EXTENSIONS = {".pdf", ".docx"}




def bulk_ingest_folder(

    folder_path: Optional[str] = None,
    reprocess_existing: bool = False
):


    if folder_path:
       folder = Path(folder_path)
    else:
    # Enterprise-RAG/server/ingestion/batch_ingestion.py
    # parents[2] = Enterprise-RAG/
      project_root = Path(__file__).resolve().parents[2]
      folder = project_root / "data" / "raw"

    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"folder not found: {folder}")

    files = [
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS
    ]
    files = sorted(files, key=lambda p: p.name.lower())

    results = []
    processed_count = 0
    skipped_count = 0

    for file_path in files:
        file_name = file_path.name
        preview = extract_preview_text(str(file_path))

        inferred_doc_type = classify_document(
                        file_name=file_name,
                        preview=preview
)
        title = file_path.stem.replace("_", " ").replace("-", " ").strip()

        existing_doc = get_document_by_file_name(

            file_name=file_name
        )

        try:
            # Case 1: existing doc and we do NOT want to reprocess
            if existing_doc and not reprocess_existing:
                skipped_count += 1
                results.append({
                    "file_name": file_name,
                    "status": "skipped_existing",
                    "document_id": str(existing_doc["_id"]),
                    "doc_type": existing_doc.get("doc_type"),
                    "reason": "Document already exists. Use reprocess_existing=true to rebuild."
                })
                continue

            # Case 2: existing doc and we DO want to reprocess
            if existing_doc and reprocess_existing:
                document_id = str(existing_doc["_id"])

                # refresh metadata in case title / inferred type / path changed
                update_document_file_metadata(
                    document_id=document_id,
                    title=title,
                    doc_type=inferred_doc_type,
                    file_path=str(file_path)
                )

                chunk_result = process_document_into_chunks(document_id)
                embed_result = embed_document_chunks(document_id)

                processed_count += 1
                results.append({
                    "file_name": file_name,
                    "status": "reprocessed",
                    "document_id": document_id,
                    "doc_type": inferred_doc_type,
                    "chunking_strategy": chunk_result.get("chunking_strategy"),
                    "total_chunks": chunk_result.get("total_chunks"),
                    "embedded_chunks": embed_result.get("embedded_chunks", 0)
                })
                continue

            # Case 3: new document
            saved_doc = create_document(

                title=title,
                doc_type=inferred_doc_type,
                file_name=file_name,
                file_path=str(file_path)
            )

            document_id = str(saved_doc["_id"])

            chunk_result = process_document_into_chunks(document_id)
            embed_result = embed_document_chunks(document_id)

            processed_count += 1
            results.append({
                "file_name": file_name,
                "status": "processed",
                "document_id": document_id,
                "doc_type": inferred_doc_type,
                "chunking_strategy": chunk_result.get("chunking_strategy"),
                "total_chunks": chunk_result.get("total_chunks"),
                "embedded_chunks": embed_result.get("embedded_chunks", 0)
            })

        except Exception as e:
            results.append({
                "file_name": file_name,
                "status": "failed",
                "doc_type": inferred_doc_type,
                "error": str(e)
            })

    return {

        "folder": str(folder),
        "total_files_found": len(files),
        "processed": processed_count,
        "skipped": skipped_count,
        "results": results
    }