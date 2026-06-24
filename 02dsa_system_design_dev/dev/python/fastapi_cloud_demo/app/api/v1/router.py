"""Aggregates the v1 routers under a single APIRouter."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import agents, chat, health, retrieval

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(agents.router)
api_router.include_router(retrieval.router)
