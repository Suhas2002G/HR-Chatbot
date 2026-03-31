from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.chat_service import ChatService, ChatServiceError

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Employee HR question")


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    retrieved_chunks: int


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        result = ChatService().answer_question(payload.question)
    except ChatServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ChatResponse(**result)
