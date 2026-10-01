"""Aggregate v1 API router."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    agents,
    attachments,
    auth,
    chat,
    health,
    notes,
    retrieval,
)

api_router = APIRouter()

# Core note-taking app
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(notes.router)
api_router.include_router(attachments.router)

# AI features
api_router.include_router(chat.router)
api_router.include_router(retrieval.router)
api_router.include_router(agents.router)
