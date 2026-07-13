from datetime import datetime
from bson import ObjectId
from db.mongo import documents_collection


def create_document(
    tenant_id: str,
    title: str,
    doc_type: str,
    file_name: str,
    file_path: str
):
    doc = {
        "tenant_id": tenant_id,
        "title": title,
        "doc_type": doc_type,
        "file_name": file_name,
        "file_path": file_path,
        "uploaded_at": datetime.utcnow(),

        # processing metadata
        "chunking_strategy": None,
        "chunk_count": 0,
        "processed_at": None
    }

    result = documents_collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def get_documents_by_tenant(tenant_id: str):
    return list(
        documents_collection.find({"tenant_id": tenant_id}).sort("uploaded_at", -1)
    )


def get_document_by_id(document_id: str):
    return documents_collection.find_one({"_id": ObjectId(document_id)})


def get_document_by_tenant_and_file_name(tenant_id: str, file_name: str):
    return documents_collection.find_one({
        "tenant_id": tenant_id,
        "file_name": file_name
    })


def update_document_chunking_info(
    document_id: str,
    chunking_strategy: str,
    chunk_count: int
):
    documents_collection.update_one(
        {"_id": ObjectId(document_id)},
        {
            "$set": {
                "chunking_strategy": chunking_strategy,
                "chunk_count": chunk_count,
                "processed_at": datetime.utcnow()
            }
        }
    )


def update_document_file_metadata(
    document_id: str,
    title: str,
    doc_type: str,
    file_path: str
):
    documents_collection.update_one(
        {"_id": ObjectId(document_id)},
        {
            "$set": {
                "title": title,
                "doc_type": doc_type,
                "file_path": file_path
            }
        }
    )