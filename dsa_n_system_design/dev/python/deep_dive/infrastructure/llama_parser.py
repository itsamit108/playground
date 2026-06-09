import os
import tempfile
from pathlib import Path

import httpx
from llama_cloud import LlamaCloud

from domain.models import ParsedPage


def parse_pdf(
    pdf_path: str | Path,
    tier: str = "agentic",
    page_range: str | None = None,
) -> tuple[list[ParsedPage], str]:
    """
    Upload PDF to LlamaParse, wait for completion, download page screenshots
    and embedded/layout images.

    Args:
        page_range: Optional page-range string, e.g. "1-3" or "1,3,5".
    Returns (pages, job_id).
    """
    api_key = os.environ["LLAMA_CLOUD_API_KEY"]
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

    job_id = result.job.id
    raw_pages = result.markdown.pages if result.markdown else []
    screenshot_urls, embedded_urls = _categorize_images(result.images_content_metadata)

    tmp_dir = Path(tempfile.mkdtemp(prefix="llamaparse_"))
    _download_images(screenshot_urls, tmp_dir)
    _download_embedded(embedded_urls, tmp_dir)

    return _build_pages(raw_pages, tmp_dir, embedded_urls), job_id


def _categorize_images(images_meta) -> tuple[dict[int, str], dict[int, list[tuple[str, str]]]]:
    """Split image metadata into screenshot_urls and embedded_urls by page."""
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


def _upload_file(client: LlamaCloud, pdf_path: Path) -> str:
    with open(pdf_path, "rb") as f:
        file_obj = client.files.create(
            file=(pdf_path.name, f, "application/pdf"),
            purpose="parse",
        )
    return file_obj.id


def _page_num_from_filename(filename: str) -> int | None:
    """Extract page number from filenames like 'page_3.jpg' or 'page_1_image_1_v2.jpg'."""
    try:
        stem = Path(filename).stem      # e.g. "page_3" or "page_1_image_1_v2"
        return int(stem.split("_")[1])
    except (IndexError, ValueError):
        return None


def _download_images(urls: dict[int, str], dest: Path) -> None:
    with httpx.Client(timeout=60) as http:
        for page_num, url in urls.items():
            resp = http.get(url)
            if resp.status_code == 200:
                (dest / f"page_{page_num}.jpg").write_bytes(resp.content)


def _download_embedded(embedded_urls: dict[int, list[tuple[str, str]]], dest: Path) -> None:
    with httpx.Client(timeout=60) as http:
        for entries in embedded_urls.values():
            for filename, url in entries:
                resp = http.get(url)
                if resp.status_code == 200:
                    (dest / filename).write_bytes(resp.content)


def _build_pages(raw_pages, tmp_dir: Path, embedded_urls: dict[int, list[tuple[str, str]]]) -> list[ParsedPage]:
    pages: list[ParsedPage] = []
    for raw in raw_pages:
        page_num = raw.page_number
        screenshot = _find_screenshot(tmp_dir, page_num)
        embedded_paths = [
            str(tmp_dir / fname)
            for fname, _ in embedded_urls.get(page_num, [])
            if (tmp_dir / fname).exists()
        ]
        pages.append(ParsedPage(
            page_number=page_num,
            markdown=getattr(raw, "markdown", "") or "",
            screenshot_path=str(screenshot) if screenshot else "",
            embedded_image_paths=embedded_paths,
        ))
    return pages


def _find_screenshot(tmp_dir: Path, page_num: int) -> Path | None:
    for candidate in (tmp_dir / f"page_{page_num}.jpg", tmp_dir / f"page_{page_num - 1}.jpg"):
        if candidate.exists():
            return candidate
    return None
