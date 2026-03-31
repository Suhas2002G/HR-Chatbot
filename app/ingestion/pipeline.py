from dataclasses import dataclass
from pathlib import Path

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.chroma_client import ChromaRepository
from app.ingestion.chunking import chunk_text
from app.ingestion.loaders import load_pdf_text
from app.services.embedding_service import EmbeddingService


@dataclass
class IngestionResult:
    indexed_documents: int
    indexed_chunks: int
    collection_name: str


class IngestionPipeline:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._repo = ChromaRepository()
        self._embedding_service = EmbeddingService()
        self._logger = get_logger(__name__)

    def run(self) -> IngestionResult:
        pdf_files = self._settings.list_policy_files()
        if not pdf_files:
            raise ValueError(f"No PDF policies found in {self._settings.hr_policies_dir}")

        self._repo.reset_collection()
        indexed_chunks = 0

        for pdf_path in pdf_files:
            indexed_chunks += self._ingest_pdf(pdf_path)

        return IngestionResult(
            indexed_documents=len(pdf_files),
            indexed_chunks=indexed_chunks,
            collection_name=self._repo.collection_name,
        )

    def _ingest_pdf(self, pdf_path: Path) -> int:
        text = load_pdf_text(pdf_path)
        chunks = chunk_text(
            text=text,
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
        )
        if not chunks:
            self._logger.warning("empty_document_skipped", extra={"source": str(pdf_path)})
            return 0

        embeddings = self._embedding_service.embed_texts(chunks)
        ids = []
        metadatas = []
        for index, _ in enumerate(chunks):
            ids.append(f"{pdf_path.stem}-{index}")
            metadatas.append(
                {
                    "document_name": pdf_path.name,
                    "source_path": str(pdf_path),
                    "section": "General",
                }
            )

        self._repo.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        self._logger.info(
            "document_indexed",
            extra={"source": str(pdf_path), "chunks": len(chunks)},
        )
        return len(chunks)
