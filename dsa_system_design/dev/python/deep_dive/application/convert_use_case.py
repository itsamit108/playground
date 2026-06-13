import asyncio
import logging
from pathlib import Path

from domain.models import GeneratedChapter
from domain import services
from infrastructure import llama_parser, gemini_generator, epub_writer

logger = logging.getLogger(__name__)


async def convert(
    pdf_path: str | Path,
    output_path: str | Path,
    page_range: str | None = None,
) -> Path:
    """
    Full pipeline: PDF → EPUB3.

    1. LlamaParse: extract per-page markdown + download page screenshots
    2. Segment pages into chapters and extract book metadata
    3. Gemini 3.5 Flash: generate XHTML for each chapter (multimodal)
    4. ebooklib: assemble and write the EPUB3 file
    """
    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    logger.info("Step 1/4: Parsing PDF with LlamaParse — %s (pages: %s)", pdf_path.name, page_range or "all")
    pages, job_id = await asyncio.to_thread(llama_parser.parse_pdf, str(pdf_path), "agentic", page_range)
    logger.info("Parsed %d pages (job %s)", len(pages), job_id)

    logger.info("Step 2/4: Segmenting into chapters and extracting metadata")
    chapters = services.segment_into_chapters(pages)
    metadata = services.extract_metadata_from_first_page(pages[0].markdown if pages else "")
    logger.info(
        "Found %d chapter(s). Title: %r, Author: %r",
        len(chapters),
        metadata.title,
        metadata.author,
    )

    logger.info("Step 3/4: Generating XHTML with Gemini 3.5 Flash")
    generated: list[GeneratedChapter] = []
    for ch in chapters:
        logger.info("  Generating chapter %d/%d: %r (%d pages)", ch.index + 1, len(chapters), ch.title, len(ch.pages))
        gen_ch = await asyncio.to_thread(gemini_generator.generate_chapter_xhtml, ch)
        generated.append(gen_ch)

    logger.info("Step 4/4: Assembling EPUB3")
    result_path = await asyncio.to_thread(epub_writer.build_epub, metadata, generated, output_path)
    logger.info("EPUB written to %s", result_path)
    return result_path
