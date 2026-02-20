"""
Configuration management for the application.
Handles both local and cloud environments.
"""
from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    GROQ_API_KEY: str = ""  # Will be set via environment variables
    GEMINI_API_KEY: str = ""  # Optional (for LLM fallback, not used for embeddings)
    
    # Environment
    ENVIRONMENT: Literal["local", "cloud", "production"] = "local"
    
    # Database
    DATABASE_URL: str = "sqlite:///./rag_system.db"
    
    # Vector DB
    VECTOR_DB_TYPE: Literal["chroma", "pinecone"] = "chroma"
    VECTOR_DB_PATH: str = "./chroma_db"
    CHROMA_DB_PATH: str | None = None  # Alias for VECTOR_DB_PATH (for backward compatibility)
    
    @model_validator(mode='after')
    def sync_chroma_db_path(self):
        """Sync CHROMA_DB_PATH to VECTOR_DB_PATH if provided."""
        if self.CHROMA_DB_PATH:
            self.VECTOR_DB_PATH = self.CHROMA_DB_PATH
        return self
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"  # Frontend URL for CORS
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: str = ".pdf,.docx,.txt"  # Comma-separated string from .env
    
    @property
    def allowed_extensions_list(self) -> list:
        """Convert comma-separated string to list."""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    # RAG Settings
    CHUNK_SIZE: int = 1000  # characters per chunk
    CHUNK_OVERLAP: int = 200  # overlap between chunks
    TOP_K_RESULTS: int = 8  # number of chunks to retrieve (increased for better retrieval)
    TOP_K_COMPLEX: int = 12  # more chunks for complex/inference questions
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()
