"""Concrete agent workflows.

* ``EpubConversionAgent`` — the flagship multi-step agent: parse PDF -> generate
  XHTML per chapter (via the LLM provider) -> assemble EPUB3. Genuinely exercises
  the ai/models, ai/rag and infra/storage layers. Runs end-to-end with the
  EchoProvider + offline parser when no keys are present.
* ``SummarizeAgent`` — a tiny generic plan/act/respond example.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.ai.agents.base import BaseAgent
from app.ai.agents.state import RunState, StepStatus
from app.ai.models.base import LLMClient, make_message
from app.ai.models.providers import GeminiProvider
from app.ai.prompts.loader import load_prompt
from app.ai.rag import document_parser
from app.core.config import Settings
from app.core.logging import get_logger
from app.schemas.agents import Chapter, GeneratedChapter, ParsedPage

logger = get_logger(__name__)

MAX_PAGES_PER_CALL = 8


# ---------------------------------------------------------------------------
# XHTML helpers
# ---------------------------------------------------------------------------
def clean_and_validate_xhtml(raw: str) -> str:
    """Strip markdown fences and validate the XHTML fragment.

    Falls back to an escaped <pre> block if the fragment is not well-formed XML,
    so EPUB assembly never breaks on bad model output.
    """
    from lxml import etree

    if raw.startswith("```"):
        lines = raw.splitlines()
        inner = lines[1:] if lines[0].startswith("```") else lines
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        raw = "\n".join(inner)

    wrapped = f"<root xmlns:epub='http://www.idpf.org/2007/ops'>{raw}</root>"
    try:
        etree.fromstring(wrapped.encode("utf-8"))
        return raw
    except etree.XMLSyntaxError:
        escaped = raw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"<pre>{escaped}</pre>"


async def _generate_chapter_xhtml(
    llm: LLMClient, chapter: Chapter, *, system_instruction: str, model: str | None
) -> GeneratedChapter:
    """Generate XHTML for a chapter, batching pages and using multimodal input
    when the provider is Gemini (passing page screenshots)."""
    pages = chapter.pages
    batches = [pages[i : i + MAX_PAGES_PER_CALL] for i in range(0, len(pages), MAX_PAGES_PER_CALL)] or [[]]
    parts: list[str] = []

    for batch in batches:
        text = "\n".join(f"--- PAGE {p.page_number} ---\n{p.markdown}\n" for p in batch)

        if isinstance(llm, GeminiProvider):
            image_bytes: list[bytes] = []
            for p in batch:
                if p.screenshot_path and Path(p.screenshot_path).exists():
                    image_bytes.append(Path(p.screenshot_path).read_bytes())
            raw = await llm.generate_multimodal(
                text=text,
                image_bytes=image_bytes,
                system_instruction=system_instruction,
                model=model,
            )
        else:
            resp = await llm.generate(
                [make_message("system", system_instruction), make_message("user", text)],
                model=model,
                temperature=0.1,
            )
            raw = str(resp.get("content", ""))

        parts.append(clean_and_validate_xhtml(raw))

    return GeneratedChapter(chapter=chapter, xhtml="\n".join(parts))


# ---------------------------------------------------------------------------
# EPUB conversion agent
# ---------------------------------------------------------------------------
class EpubConversionAgent(BaseAgent):
    """Multi-step workflow: parse -> generate sections -> assemble EPUB."""

    name = "epub_conversion"

    def __init__(self, llm: LLMClient, settings: Settings):
        super().__init__(llm)
        self.settings = settings

    async def plan(self, state: RunState) -> list[str]:
        return ["parse", "segment", "generate", "assemble"]

    async def act(self, step: str, state: RunState) -> None:
        if step == "parse":
            await self._parse(state)
        elif step == "segment":
            self._segment(state)
        elif step == "generate":
            await self._generate(state)
        elif step == "assemble":
            self._assemble(state)

    async def _parse(self, state: RunState) -> None:
        import asyncio

        pdf_path = state.inputs["pdf_path"]
        page_range = state.inputs.get("page_range")
        if self.settings.has_llama_key:
            pages = await asyncio.to_thread(
                document_parser.parse_pdf_llama,
                pdf_path,
                api_key=self.settings.llama_cloud_api_key,
                tier=self.settings.llama_parse_tier,
                page_range=page_range,
            )
            detail = f"LlamaParse: {len(pages)} page(s)"
        else:
            pages = document_parser.parse_pdf_offline(pdf_path)
            detail = f"offline parser: {len(pages)} page(s)"
        state.scratch["pages"] = pages
        state.record("parse", detail=detail)

    def _segment(self, state: RunState) -> None:
        pages: list[ParsedPage] = state.scratch["pages"]
        chapters = document_parser.segment_into_chapters(pages)
        metadata = document_parser.extract_metadata_from_first_page(
            pages[0].markdown if pages else ""
        )
        state.scratch["chapters"] = chapters
        state.scratch["metadata"] = metadata
        state.record("segment", detail=f"{len(chapters)} chapter(s); title={metadata.title!r}")

    async def _generate(self, state: RunState) -> None:
        chapters: list[Chapter] = state.scratch["chapters"]
        system_instruction = load_prompt("epub_author")
        generated: list[GeneratedChapter] = []
        for ch in chapters:
            gen = await _generate_chapter_xhtml(
                self.llm, ch, system_instruction=system_instruction, model=self.settings.llm_model
            )
            generated.append(gen)
        state.scratch["generated"] = generated
        state.record("generate", detail=f"generated {len(generated)} chapter(s) via {getattr(self.llm, 'name', 'llm')}")

    def _assemble(self, state: RunState) -> None:
        from app.infra import storage

        metadata = state.scratch["metadata"]
        generated = state.scratch["generated"]
        output_path = Path(state.inputs["output_path"])
        result = storage.build_epub(metadata, generated, output_path)
        state.output = {"output_path": str(result), "title": metadata.title}
        state.record("assemble", detail=f"EPUB written to {result}")

    async def respond(self, state: RunState) -> dict[str, Any]:
        return state.output


# ---------------------------------------------------------------------------
# Generic summarize agent (demonstrates plan/act/respond with the LLM)
# ---------------------------------------------------------------------------
class SummarizeAgent(BaseAgent):
    name = "summarize"

    async def plan(self, state: RunState) -> list[str]:
        return ["summarize"]

    async def act(self, step: str, state: RunState) -> None:
        text = str(state.inputs.get("text", state.goal))
        resp = await self.llm.generate(
            [
                make_message("system", "Summarize the user's text in one short paragraph."),
                make_message("user", text),
            ]
        )
        state.scratch["summary"] = str(resp.get("content", ""))
        state.record("summarize", detail="produced summary")

    async def respond(self, state: RunState) -> dict[str, Any]:
        return {"summary": state.scratch.get("summary", "")}
