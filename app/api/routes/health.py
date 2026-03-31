from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str | int]:
    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "documents_path": str(settings.hr_policies_dir),
        "document_count": len(settings.list_policy_files()),
        "vector_store_path": str(settings.chroma_persist_dir),
    }
