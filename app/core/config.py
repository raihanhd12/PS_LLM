from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Document AI Assistant API"

    # Embedding API Configuration
    EMBEDDING_API_URL: str = Field(None, env="API_URL")
    EMBEDDING_API_KEY: Optional[str] = Field(None, env="API_KEY")

    # Digital Ocean GenAI Agent API configuration
    DO_API_URL: str = Field(None, env="DO_API_URL")
    DO_API_KEY: str = Field(None, env="DO_API_KEY")
    DO_CHATBOT_ID: str = Field(None, env="DO_CHATBOT_ID")

    # Ollama Configuration
    OLLAMA_API_URL: str = Field(None, env="OLLAMA_API_URL")
    OLLAMA_MODEL: str = Field(None, env="OLLAMA_MODEL")
    OLLAMA_MODEL_TITLE: str = Field(None, env="OLLAMA_MODEL_TITLE")

    # Database Configuration
    POSTGRES_SERVER: str = Field(None, env="POSTGRES_SERVER")
    POSTGRES_PORT: str = Field(None, env="POSTGRES_PORT")
    POSTGRES_USER: str = Field(None, env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(None, env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(None, env="POSTGRES_DB")

    @property
    def DATABASE_URL(self) -> str:
        """Get database connection string"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
