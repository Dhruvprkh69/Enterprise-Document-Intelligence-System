"""
Configuration management for the application.
Handles both local and cloud environments.
"""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    GROQ_API_KEY: str
    GEMINI_API_KEY: str = ""
    
    # Environment
    ENVIRONMENT: Literal["local", "cloud"] = "local"
    
    # Database
    DATABASE_URL: str = "sqlite:///./rag_system.db"
    
    # Vector DB
    VECTOR_DB_TYPE: Literal["chroma", "pinecone"] = "chroma"
    VECTOR_DB_PATH: str = "./chroma_db"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt"]
    
    # RAG Settings
    CHUNK_SIZE: int = 1000  # characters per chunk
    CHUNK_OVERLAP: int = 200  # overlap between chunks
    TOP_K_RESULTS: int = 5  # number of chunks to retrieve
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
