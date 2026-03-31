from collections.abc import Sequence

import chromadb

from app.core.config import get_settings


class ChromaRepository:
    def __init__(self) -> None:
        settings = get_settings()
        settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(settings.chroma_persist_dir))
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"description": "HR policies collection"},
        )

    @property
    def collection_name(self) -> str:
        return self._collection.name

    def reset_collection(self) -> None:
        self._client.delete_collection(self._collection.name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection.name,
            metadata={"description": "HR policies collection"},
        )

    def upsert(
        self,
        ids: Sequence[str],
        documents: Sequence[str],
        embeddings: Sequence[Sequence[float]],
        metadatas: Sequence[dict[str, str]],
    ) -> None:
        self._collection.upsert(
            ids=list(ids),
            documents=list(documents),
            embeddings=[list(embedding) for embedding in embeddings],
            metadatas=list(metadatas),
        )

    def query(self, query_embedding: Sequence[float], top_k: int) -> dict:
        return self._collection.query(
            query_embeddings=[list(query_embedding)],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
