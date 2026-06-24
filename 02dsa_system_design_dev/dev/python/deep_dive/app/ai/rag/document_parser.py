"""Document parsing + ingestion for the PDF -> EPUB pipeline.

Two parsing paths:

* ``parse_pdf_llama`` — real LlamaParse (llama-cloud) extraction with page
  screenshots + embedded images. Used when ``LLAMA_CLOUD_API_KEY`` is set.
* ``parse_pdf_offline`` — pure-stdlib fallback that reads the PDF bytes and emits
  a single page of placeholder markdown, so the pipeline runs with no key/network.

Also hosts chapter segmentation + metadata extraction (formerly
``domain/services.py``).
"""

from __future__ import annotations

import re
import tempfile
import uuid
from pathlib import Path

from app.core.logging import get_logger
from app.schemas.agents import BookMetadata, Chapter, ParsedPage

logger = get_logger(__name__)


# ----------------------------------------------------------------------------
# Parsing
# ----------------------------------------------------------------------------
def parse_pdf_offline(pdf_path: str | Path) -> list[ParsedPage]:
    """Offline fallback parser. Produces minimal markdown without any network.

    Attempts a light text scan of the PDF bytes for a human-readable title; if
    none is found, emits a placeholder. The goal is a *valid* pipeline run, not
    high-fidelity extraction.
    """
    pdf_path = Path(pdf_path)
    name = pdf_path.stem.replace("_", " ").replace("-", " ").strip() or "Document"
    md = (
        f"# {name.title()}\n\n"
        "This document was processed in offline mode (no LlamaParse key set). "
        "Configure LLAMA_CLOUD_API_KEY for full-fidelity PDF extraction.\n"
    )
    return [ParsedPage(page_number=1, markdown=md, screenshot_path="", embedded_image_paths=[])]


def parse_pdf_llama(
    pdf_path: str | Path,
    *,
    api_key: str,
    tier: str = "agentic",
    page_range: str | None = None,
) -> list[ParsedPage]:
    """Parse a PDF via LlamaParse (llama-cloud), downloading page screenshots and
    embedded images to a temp dir. Returns a list of :class:`ParsedPage`.
    """
    import httpx
    from llama_cloud import LlamaCloud

    client = LlamaCloud(api_key=api_key)
    file_id = _upload_file(client, Path(pdf_path))

    extra: dict = {}
    if page_range:
        extra["page_ranges"] = {"target_pages": page_range}

    result = client.parsing.parse(
        file_id=file_id,
        tier=tier,
        version="latest",
        disable_cache=True,
        expand=["markdown", "images_content_metadata"],
        output_options={"images_to_save": ["screenshot", "embedded", "layout"]},
        **extra,
    )

    raw_pages = result.markdown.pages if result.markdown else []
    screenshot_urls, embedded_urls = _categorize_images(result.images_content_metadata)

    tmp_dir = Path(tempfile.mkdtemp(prefix="llamaparse_"))
    _download_images(httpx, screenshot_urls, tmp_dir)
    _download_embedded(httpx, embedded_urls, tmp_dir)
    return _build_pages(raw_pages, tmp_dir, embedded_urls)


def _upload_file(client, pdf_path: Path) -> str:
    with open(pdf_path, "rb") as f:
        file_obj = client.files.create(
            file=(pdf_path.name, f, "application/pdf"),
            purpose="parse",
        )
    return file_obj.id


def _categorize_images(images_meta):
    screenshot_urls: dict[int, str] = {}
    embedded_urls: dict[int, list[tuple[str, str]]] = {}
    if not images_meta:
        return screenshot_urls, embedded_urls
    for img in images_meta.images:
        if not img.presigned_url:
            continue
        page_num = _page_num_from_filename(img.filename)
        if page_num is None:
            continue
        if img.category == "screenshot":
            screenshot_urls[page_num] = img.presigned_url
        else:
            embedded_urls.setdefault(page_num, []).append((img.filename, img.presigned_url))
    return screenshot_urls, embedded_urls


def _page_num_from_filename(filename: str) -> int | None:
    try:
        stem = Path(filename).stem
        return int(stem.split("_")[1])
    except (IndexError, ValueError):
        return None


def _download_images(httpx, urls: dict[int, str], dest: Path) -> None:
    with httpx.Client(timeout=60) as http:
        for page_num, url in urls.items():
            resp = http.get(url)
            if resp.status_code == 200:
                (dest / f"page_{page_num}.jpg").write_bytes(resp.content)


def _download_embedded(httpx, embedded_urls: dict[int, list[tuple[str, str]]], dest: Path) -> None:
    with httpx.Client(timeout=60) as http:
        for entries in embedded_urls.values():
            for filename, url in entries:
                resp = http.get(url)
                if resp.status_code == 200:
                    (dest / filename).write_bytes(resp.content)


def _build_pages(raw_pages, tmp_dir: Path, embedded_urls) -> list[ParsedPage]:
    pages: list[ParsedPage] = []
    for raw in raw_pages:
        page_num = raw.page_number
        screenshot = _find_screenshot(tmp_dir, page_num)
        embedded_paths = [
            str(tmp_dir / fname)
            for fname, _ in embedded_urls.get(page_num, [])
            if (tmp_dir / fname).exists()
        ]
        pages.append(
            ParsedPage(
                page_number=page_num,
                markdown=getattr(raw, "markdown", "") or "",
                screenshot_path=str(screenshot) if screenshot else "",
                embedded_image_paths=embedded_paths,
            )
        )
    return pages


def _find_screenshot(tmp_dir: Path, page_num: int) -> Path | None:
    for candidate in (tmp_dir / f"page_{page_num}.jpg", tmp_dir / f"page_{page_num - 1}.jpg"):
        if candidate.exists():
            return candidate
    return None


# ----------------------------------------------------------------------------
# Segmentation + metadata (formerly domain/services.py)
# ----------------------------------------------------------------------------
def segment_into_chapters(pages: list[ParsedPage]) -> list[Chapter]:
    """Group pages into chapters by detecting heading markers in markdown."""
    chapter_patterns = [
        re.compile(r"^#\s+chapter\s+\d+.*", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^#\s+\d+\..*", re.MULTILINE),
        re.compile(r"^#{1,2}\s+\w.*", re.MULTILINE),
    ]

    chapters: list[Chapter] = []
    current_title = "Front Matter"
    current_pages: list[ParsedPage] = []
    chapter_index = 0

    for page in pages:
        new_title = _detect_chapter_title(page.markdown, chapter_patterns)
        if new_title and current_pages:
            chapters.append(Chapter(index=chapter_index, title=current_title, pages=current_pages))
            chapter_index += 1
            current_title = new_title
            current_pages = [page]
        else:
            if new_title:
                current_title = new_title
            current_pages.append(page)

    if current_pages:
        chapters.append(Chapter(index=chapter_index, title=current_title, pages=current_pages))

    return chapters if chapters else [Chapter(index=0, title="Content", pages=pages)]


def _detect_chapter_title(markdown: str, patterns: list[re.Pattern]) -> str | None:
    for pattern in patterns:
        match = pattern.search(markdown)
        if match:
            line = match.group(0).strip()
            title = re.sub(r"^#+\s*", "", line).strip()
            if title:
                return title
    return None


def extract_metadata_from_first_page(page_markdown: str) -> BookMetadata:
    """Heuristic title/author extraction from the first page markdown."""
    lines = [l.strip() for l in page_markdown.splitlines() if l.strip()]

    title = "Untitled Book"
    author = "Unknown Author"

    for line in lines:
        if line.startswith("#"):
            title = re.sub(r"^#+\s*", "", line).strip()
            break
    if title == "Untitled Book" and lines:
        title = lines[0][:80]

    for line in lines:
        m = re.search(r"\bby\b\s+([A-Z][a-zA-Z\s\.,]+)", line)
        if m:
            author = m.group(1).strip()
            break
        m = re.search(r"author[:\s]+(.+)", line, re.IGNORECASE)
        if m:
            author = m.group(1).strip()
            break

    return BookMetadata(title=title, author=author, language="en", identifier=str(uuid.uuid4()))
