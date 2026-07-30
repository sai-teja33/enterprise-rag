from sentence_transformers import CrossEncoder
from core.config import settings


class ChunkReranker:
    def __init__(self):
        self.model = None

    def _load_model(self):
        if self.model is None:
            print(f"Loading CrossEncoder: {settings.CROSS_ENCODER_MODEL}")
            self.model = CrossEncoder(settings.CROSS_ENCODER_MODEL)

    def rerank(
        self,
        question: str,
        chunks: list[dict],
        top_k: int = 5
    ) -> list[dict]:
         # Load the model only on first use
        self._load_model()

        if not chunks:
            return []

        # Build (question, chunk) pairs
        pairs = [
            (question, chunk.get("chunk_text", ""))
            for chunk in chunks
        ]

        # Compute relevance scores
        scores = self.model.predict(
            pairs,
            show_progress_bar=False
        )

        # Attach scores
        reranked_chunks = []
        for chunk, score in zip(chunks, scores):
            chunk_copy = dict(chunk)
            chunk_copy["rerank_score"] = float(score)
            reranked_chunks.append(chunk_copy)

        # Highest score first
        reranked_chunks.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return reranked_chunks[:top_k]


reranker = ChunkReranker()