from app.core.config import get_settings
from app.db.chroma_client import ChromaRepository
from app.models.document import DocumentChunk
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._repo = ChromaRepository()
        self._embedding_service = EmbeddingService()

    def retrieve(self, question: str) -> list[DocumentChunk]:
        query_embedding = self._embedding_service.embed_text(question)
        results = self._repo.query(
            query_embedding=query_embedding,
            top_k=self._settings.retrieval_top_k,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        ids = results.get("ids", [[]])[0] if "ids" in results else []

        chunks: list[DocumentChunk] = []
        for index, document in enumerate(documents):
            metadata = metadatas[index] if index < len(metadatas) else {}
            chunk_id = ids[index] if index < len(ids) else f"chunk-{index}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_name=str(metadata.get("document_name", "Unknown")),
                    source_path=str(metadata.get("source_path", "")),
                    text=document,
                    section=str(metadata.get("section", "General")),
                )
            )
        return chunks
