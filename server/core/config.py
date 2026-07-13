
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    MONGODB_URI: str
    DB_NAME: str

    # LLM / provider config
    GROQ_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    ANSWER_LLM_PROVIDER: str = "openai"   # "openai" or "groq"
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    GROQ_CHAT_MODEL: str = "llama-3.3-70b-versatile"

    # Retrieval / embedding models
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_BATCH_SIZE: int = 16
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Frontend / deployment
    FRONTEND_ORIGINS: str = "http://localhost:4200,http://127.0.0.1:4200"

    @property
    def frontend_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()