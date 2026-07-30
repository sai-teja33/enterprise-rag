from db.mongo import chunks_collection

TEXT_INDEX_NAME = "chunk_text_index"


def retrieve_text_chunks(

    question: str,
    top_k: int = 5,
    doc_type: str | None = None
):
    search_clause = {
        "text": {
            "query": question,
            "path": ["chunk_text", "title"]
        }
    }

    compound = {
        "must": [search_clause]
    }

    if doc_type:
        compound["filter"] = [
            {
                "equals": {
                    "path": "doc_type",
                    "value": doc_type
                }
            }
        ]

    pipeline = [
        {
            "$search": {
                "index": TEXT_INDEX_NAME,
                "compound": compound
            }
        },
        {
            "$limit": top_k
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
                "score": {"$meta": "searchScore"}
            }
        }
    ]

    return list(chunks_collection.aggregate(pipeline))