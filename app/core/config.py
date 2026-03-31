from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HR Chatbot API"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    hr_policies_dir: Path = Field(default=Path("data/hr_policies_pdf"))
    chroma_persist_dir: Path = Field(default=Path("data/chroma"))
    chroma_collection: str = "hr_policies"
    gemini_api_key: str = ""
    gemini_chat_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    retrieval_top_k: int = 4
    chunk_size: int = 1200
    chunk_overlap: int = 150

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("hr_policies_dir", "chroma_persist_dir", mode="before")
    @classmethod
    def _resolve_project_path(cls, value: str | Path) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()

    def list_policy_files(self) -> list[Path]:
        if not self.hr_policies_dir.exists():
            return []
        return sorted(self.hr_policies_dir.glob("*.pdf"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
