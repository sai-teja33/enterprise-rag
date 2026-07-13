from sentence_transformers import SentenceTransformer
from core.config import settings


class E5Embedder:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # E5 expects "passage:" prefix for documents
        formatted_texts = [f"passage: {text}" for text in texts]
        embeddings = self.model.encode(
            formatted_texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        formatted_query = f"query: {query}"
        embedding = self.model.encode(
            formatted_query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding.tolist()


embedder = E5Embedder()