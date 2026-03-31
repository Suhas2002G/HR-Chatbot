from google import genai

from app.core.config import get_settings


class EmbeddingService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required to generate embeddings.")
        self._model = settings.gemini_embedding_model
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def embed_text(self, text: str) -> list[float]:
        response = self._client.models.embed_content(
            model=self._model,
            contents=text,
        )
        return list(response.embeddings[0].values)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self._client.models.embed_content(
            model=self._model,
            contents=texts,
        )
        return [list(item.values) for item in response.embeddings]
