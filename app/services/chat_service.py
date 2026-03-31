from app.services.gemini_service import GeminiService
from app.services.prompt_service import PromptService
from app.services.retrieval_service import RetrievalService


class ChatServiceError(Exception):
    """Raised when the chatbot cannot process a request."""


class ChatService:
    def __init__(self) -> None:
        self._retrieval_service = RetrievalService()
        self._prompt_service = PromptService()
        self._gemini_service = GeminiService()

    def answer_question(self, question: str) -> dict[str, str | list[str] | int]:
        chunks = self._retrieval_service.retrieve(question)
        if not chunks:
            raise ChatServiceError(
                "No indexed policy content found. Run document ingestion before using chat."
            )

        prompt = self._prompt_service.build(question, chunks)
        answer = self._gemini_service.generate_answer(prompt)
        if not answer:
            raise ChatServiceError("Gemini returned an empty response.")

        sources = []
        for chunk in chunks:
            if chunk.document_name not in sources:
                sources.append(chunk.document_name)

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": len(chunks),
        }
