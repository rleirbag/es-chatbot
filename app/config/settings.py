from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    model_config = SettingsConfigDict(env_file='.env')

    DATABASE_URL: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_SECRET_KEY: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_DOMAIN: str
    GOOGLE_FOLDER_NAME: str
    LLM_PROVIDER: str
    LLM_SYSTEM_PROMPT: str
    ANTHROPIC_API_KEY: Optional[str]
    ANTHROPIC_MODEL: Optional[str]
    OLLAMA_API_URL: str
    OLLAMA_MODEL: str
    OLLAMA_TIMEOUT: int
    OPENAI_API_KEY: Optional[str]
    RAG_CHUNK_SIZE: int
    RAG_CHUNK_OVERLAP: int
    BATCH_SIZE: int
    CHROMA_HOST: str
    CHROMA_PORT: int
    CHROMA_COLLECTION: str
