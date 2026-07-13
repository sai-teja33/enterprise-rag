from langchain_openai import OpenAIEmbeddings
from core.config import settings


class OpenAIEmbedder:
    def __init__(self):
        self.model = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.OPENAI_API_KEY
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.embed_documents(texts)

    def embed_query(self, query: str) -> list[float]:
        return self.model.embed_query(query)


embedder = OpenAIEmbedder()