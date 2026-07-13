# from sentence_transformers import CrossEncoder
# from core.config import settings


# class ChunkReranker:
#     def __init__(self):
#         self.model = CrossEncoder(settings.RERANKER_MODEL)

#     def rerank(self, question: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
#         if not chunks:
#             return []

#         pairs = []
#         for chunk in chunks:
#             chunk_text = chunk.get("chunk_text", "")
#             pairs.append((question, chunk_text))

#         scores = self.model.predict(pairs)

#         reranked = []
#         for chunk, score in zip(chunks, scores):
#             chunk_copy = dict(chunk)
#             chunk_copy["rerank_score"] = float(score)
#             reranked.append(chunk_copy)

#         reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
#         return reranked[:top_k]


# reranker = ChunkReranker()

class ChunkReranker:
    def rerank(self, question: str, chunks: list[dict], top_k: int = 5):
        # Skip ML reranking on the free deployment.
        return chunks[:top_k]


reranker = ChunkReranker()