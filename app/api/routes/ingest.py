from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ingestion.pipeline import IngestionPipeline, IngestionResult

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestResponse(BaseModel):
    indexed_documents: int
    indexed_chunks: int
    collection_name: str


@router.post("/", response_model=IngestResponse)
def ingest_documents() -> IngestResponse:
    try:
        result: IngestionResult = IngestionPipeline().run()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Document ingestion failed.") from exc

    return IngestResponse(
        indexed_documents=result.indexed_documents,
        indexed_chunks=result.indexed_chunks,
        collection_name=result.collection_name,
    )
