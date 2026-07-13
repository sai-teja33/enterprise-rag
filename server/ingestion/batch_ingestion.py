from pathlib import Path
from typing import Optional

from db.mongo import tenants_collection
from db.repositories.document_repo import (
    create_document,
    get_document_by_tenant_and_file_name,
    update_document_file_metadata
)
from ingestion.pipeline import process_document_into_chunks, embed_document_chunks


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def infer_doc_type_from_filename(file_name: str) -> str:
    """
    Very simple filename-based doc type inference.
    You can improve this later.
    """
    name = file_name.lower()

    if "leave" in name:
        return "leave_policy"
    if "insurance" in name or "medical" in name or "health" in name:
        return "insurance_policy"
    if "travel" in name or "reimburse" in name or "expense" in name:
        return "travel_policy"
    if "conduct" in name:
        return "code_of_conduct"
    if "handbook" in name or "employee" in name:
        return "employee_handbook"

    # default fallback
    return "employee_handbook"


def bulk_ingest_tenant_folder(
    tenant_slug: str,
    folder_path: Optional[str] = None,
    reprocess_existing: bool = False
):
    tenant = tenants_collection.find_one({"slug": tenant_slug})
    if tenant is None:
        raise ValueError("Tenant not found")

    tenant_id = str(tenant["_id"])

    if folder_path:
        folder = Path(folder_path)
    else:
        folder = Path("data/raw") / tenant_slug

    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Tenant folder not found: {folder}")

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
        inferred_doc_type = infer_doc_type_from_filename(file_name)
        title = file_path.stem.replace("_", " ").replace("-", " ").strip()

        existing_doc = get_document_by_tenant_and_file_name(
            tenant_id=tenant_id,
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
                    "reason": "Document already exists for this tenant. Use reprocess_existing=true to rebuild."
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
                tenant_id=tenant_id,
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
        "tenant": tenant_slug,
        "folder": str(folder),
        "total_files_found": len(files),
        "processed": processed_count,
        "skipped": skipped_count,
        "results": results
    }