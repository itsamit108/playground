import re
import uuid
from domain.models import ParsedPage, Chapter, BookMetadata


def segment_into_chapters(pages: list[ParsedPage]) -> list[Chapter]:
    """
    Group pages into chapters by detecting heading markers in markdown.
    Falls back to treating the entire document as one chapter if no headings found.
    """
    # Patterns that indicate a new chapter starts on this page
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
            # Extract the heading text (strip leading #s and whitespace)
            line = match.group(0).strip()
            title = re.sub(r"^#+\s*", "", line).strip()
            if title:
                return title
    return None


def extract_metadata_from_first_page(page_markdown: str) -> BookMetadata:
    """
    Heuristic extraction of title/author from the first page's markdown.
    Returns sensible defaults if extraction fails.
    """
    lines = [l.strip() for l in page_markdown.splitlines() if l.strip()]

    title = "Untitled Book"
    author = "Unknown Author"

    # First non-empty heading line is likely the title
    for line in lines:
        if line.startswith("#"):
            title = re.sub(r"^#+\s*", "", line).strip()
            break
    if title == "Untitled Book" and lines:
        title = lines[0][:80]

    # Look for "by <Name>" or "Author:" patterns
    for line in lines:
        m = re.search(r"\bby\b\s+([A-Z][a-zA-Z\s\.,]+)", line)
        if m:
            author = m.group(1).strip()
            break
        m = re.search(r"author[:\s]+(.+)", line, re.IGNORECASE)
        if m:
            author = m.group(1).strip()
            break

    return BookMetadata(
        title=title,
        author=author,
        language="en",
        identifier=str(uuid.uuid4()),
    )
