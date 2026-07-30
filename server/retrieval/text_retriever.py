from db.mongo import chunks_collection

TEXT_INDEX_NAME = "chunk_text_index"


def retrieve_text_chunks(

    question: str,
    top_k: int = 5
):
    pipeline = [
        {
            "$search": {
                "index": TEXT_INDEX_NAME,
                "compound": {
                    "must": [
                        {
                            "text": {
                                "query": question,
                                "path": ["chunk_text", "title", "doc_type"]
                            }
                        }
                    ],
                    
                }
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
                "page_number": 1,
                "chunk_index": 1,
                "chunk_text": 1,
                "chunk_size": 1,
                "score": {"$meta": "searchScore"}
            }
        }
    ]

    return list(chunks_collection.aggregate(pipeline))