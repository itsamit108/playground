"""Shared schemas: auth + notes + attachments DTOs and common envelopes."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ── Health ──────────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


# ── Auth ────────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


# ── Notes ───────────────────────────────────────────────────────────────────
class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    content: str = ""
    is_pinned: bool = False


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=256)
    content: str | None = None
    is_pinned: bool | None = None


class AttachmentResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    attachments: list[AttachmentResponse] = []


class NoteListResponse(BaseModel):
    notes: list[NoteResponse]
    total: int
    page: int
    page_size: int
