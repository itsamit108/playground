"""Chat endpoint: ask a question grounded in your own notes (RAG)."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep, SettingsDep
from app.schemas.chat import ChatRequest, ChatResponse, Citation
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["AI: Chat"])


@router.post("", response_model=ChatResponse, summary="Ask the notes assistant")
async def chat(
    body: ChatRequest,
    current_user: CurrentUser,
    session: SessionDep,
    settings: SettingsDep,
) -> ChatResponse:
    result = await chat_service.ask(
        session,
        current_user,
        message=body.message,
        session_id=body.session_id,
        top_k=body.top_k,
        settings=settings,
    )
    return ChatResponse(
        answer=result.answer,
        citations=[
            Citation(
                note_id=c.note_id,
                note_title=c.note_title,
                snippet=c.text,
                score=c.score,
            )
            for c in result.citations
        ],
        model=result.model,
        session_id=result.session_id,
    )
