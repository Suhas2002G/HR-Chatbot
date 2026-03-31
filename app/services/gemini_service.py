from google import genai

from app.core.config import get_settings


class GeminiService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required to generate answers.")
        self._model = settings.gemini_chat_model
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def generate_answer(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
        )
        return (response.text or "").strip()
