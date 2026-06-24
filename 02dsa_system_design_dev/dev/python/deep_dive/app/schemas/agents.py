"""Agent + PDF->EPUB conversion schemas.

The flagship AI feature (PDF -> EPUB3) is exposed as an *agent workflow*, so its
request/response models live alongside the generic agent run models.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


# --- Generic agent run ---
class AgentRunRequest(BaseModel):
    goal: str = Field(..., min_length=1)
    inputs: dict[str, Any] = Field(default_factory=dict)


class AgentStep(BaseModel):
    name: str
    status: Literal["ok", "error", "skipped"] = "ok"
    detail: str = ""


class AgentRunResponse(BaseModel):
    workflow: str
    status: Literal["completed", "failed"]
    output: dict[str, Any] = Field(default_factory=dict)
    steps: list[AgentStep] = Field(default_factory=list)


# --- PDF -> EPUB conversion ---
ConversionStatus = Literal["processing", "done", "error"]


class ConversionStart(BaseModel):
    job_id: str
    status: ConversionStatus


class ConversionStatusResponse(BaseModel):
    job_id: str
    status: ConversionStatus
    download_url: str | None = None
    error: str | None = None
    steps: list[AgentStep] = Field(default_factory=list)


# --- Book domain models (formerly domain/models.py) ---
class ParsedPage(BaseModel):
    page_number: int
    markdown: str
    screenshot_path: str = ""
    embedded_image_paths: list[str] = Field(default_factory=list)


class Chapter(BaseModel):
    index: int
    title: str
    pages: list[ParsedPage] = Field(default_factory=list)


class BookMetadata(BaseModel):
    title: str
    author: str
    language: str = "en"
    subject: str = ""
    identifier: str = ""


class GeneratedChapter(BaseModel):
    chapter: Chapter
    xhtml: str
