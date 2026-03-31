from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.ingest import router as ingest_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)

    logger.info(
        "application_startup",
        extra={
            "app_env": settings.app_env,
            "hr_policies_dir": str(settings.hr_policies_dir),
        },
    )

    app.state.settings = settings
    yield

    logger.info("application_shutdown")


settings = get_settings()
project_root = Path(__file__).resolve().parents[1]
static_dir = project_root / "static"

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(static_dir / "index.html")


app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(chat_router, prefix=settings.api_prefix)
app.include_router(ingest_router, prefix=settings.api_prefix)
