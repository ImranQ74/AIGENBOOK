"""
Configuration management for RAG chatbot backend.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Qdrant vector database
    qdrant_url: Optional[str] = None  # Use in-memory if None
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "aigenbook_chunks"

    # Neon PostgreSQL (for user data)
    neon_database_url: Optional[str] = None

    # Embedding model
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_device: str = "cpu"  # or "cuda"

    # LLM configuration (free-tier friendly)
    llm_provider: str = "transformers"  # or "openai"
    llm_model: str = "microsoft/Phi-3-mini-4k-instruct"
    llm_api_base: Optional[str] = None
    llm_api_key: Optional[str] = None

    # Chunking configuration
    chunk_size: int = 500
    chunk_overlap: int = 50

    # RAG configuration
    top_k: int = 5
    similarity_threshold: float = 0.5

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
