from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Type


class Settings(BaseSettings):

    # App Config settings
    app_name: str = "Chat Application"
    admin_email: str = "annaduraihariprasanth@gmail.com"

    # TODO : Load more env variables here as needed

    # DB Config settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    # Security settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    SECRET_KEY: str

    API_BASE_URL: str = "http://localhost:8000"
    AZURE_STORAGE_CONNECTION_STRING: str

    # Qdrant Config settings
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: str = "6333"  # gRPC port

    # Optional LLM settings for answer generation
    LLM_API_URL: str | None = None
    LLM_API_KEY: str | None = None
    LLM_MODEL: str | None = None

    # Hugging Face Settings
    HF_KEY: str | None = None
    HF_API_KEY: str | None = None
    HUGGINGFACE_API_KEY: str | None = None
    HF_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    HF_CHAT_MODEL: str = "meta-llama/Llama-3.2-3B-Instruct"

    @property
    def HUGGINGFACE_TOKEN(self) -> str | None:
        token = self.HF_KEY or self.HF_API_KEY or self.HUGGINGFACE_API_KEY
        return token.strip("\"'") if token else None

    # Langfuse Observability Settings
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_BASE_URL: str | None = "https://us.cloud.langfuse.com"
    LANGFUSE_HOST: str | None = None
    LANGFUSE_TRACING_ENABLED: bool = True

    @property
    def LANGFUSE_CLEAN_PUBLIC_KEY(self) -> str | None:
        return self.LANGFUSE_PUBLIC_KEY.strip("\"'") if self.LANGFUSE_PUBLIC_KEY else None

    @property
    def LANGFUSE_CLEAN_SECRET_KEY(self) -> str | None:
        return self.LANGFUSE_SECRET_KEY.strip("\"'") if self.LANGFUSE_SECRET_KEY else None

    @property
    def LANGFUSE_HOST_URL(self) -> str:
        url = self.LANGFUSE_BASE_URL or self.LANGFUSE_HOST or "https://us.cloud.langfuse.com"
        return url.strip("\"'")

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, env_nested_delimiter="__", extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache(maxsize=1)
def get_settings(settings_class: Type[Settings] = Settings) -> Settings:
    return settings_class()


settings = get_settings()
