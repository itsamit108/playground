import mimetypes
import re
from pathlib import Path

from ebooklib import epub

from domain.models import BookMetadata, GeneratedChapter

XHTML_TEMPLATE = """\
<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops"
      xmlns:math="http://www.w3.org/1998/Math/MathML"
      xml:lang="{lang}">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="../assets/stylesheet.css"/>
</head>
<body>
{body}
</body>
</html>"""


def build_epub(
    metadata: BookMetadata,
    generated_chapters: list[GeneratedChapter],
    output_path: str | Path,
    assets_dir: Path | None = None,
) -> Path:
    """
    Assemble and write a standards-compliant EPUB3 file.
    Returns the path to the written file.
    """
    book = epub.EpubBook()
    book.set_identifier(metadata.identifier or "unknown-id")
    book.set_title(metadata.title)
    book.set_language(metadata.language)
    book.add_author(metadata.author)
    if metadata.subject:
        book.add_metadata("DC", "subject", metadata.subject)

    # Add stylesheet
    css_path = (assets_dir or Path(__file__).parent.parent / "assets") / "stylesheet.css"
    css_content = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    css_item = epub.EpubItem(
        uid="stylesheet",
        file_name="assets/stylesheet.css",
        media_type="text/css",
        content=css_content.encode("utf-8"),
    )
    book.add_item(css_item)

    chapter_items: list[epub.EpubHtml] = []
    all_page_ids: list[tuple[str, str]] = []  # (file_name#id, title)
    added_images: set[str] = set()

    for gen_ch in generated_chapters:
        ch = gen_ch.chapter
        file_name = f"chap_{ch.index:03d}.xhtml"
        title = ch.title or f"Chapter {ch.index + 1}"

        xhtml_content = XHTML_TEMPLATE.format(
            lang=metadata.language,
            title=title,
            body=gen_ch.xhtml,
        )

        ch_item = epub.EpubHtml(
            uid=f"chapter_{ch.index}",
            title=title,
            file_name=file_name,
            lang=metadata.language,
        )
        ch_item.content = xhtml_content.encode("utf-8")
        ch_item.add_item(css_item)
        book.add_item(ch_item)
        chapter_items.append(ch_item)

        # Embed all downloaded images for pages in this chapter
        for page in ch.pages:
            for img_path in page.embedded_image_paths:
                _add_image(book, Path(img_path), added_images)

        # Collect page-break spans for page-list nav
        for m in re.finditer(r'epub:type="pagebreak"\s+id="(page-\d+)"\s+title="(\d+)"', gen_ch.xhtml):
            all_page_ids.append((f"{file_name}#{m.group(1)}", m.group(2)))

    # TOC — epub.Link(href, title, uid) — uid must not be None
    book.toc = [epub.Link(item.file_name, item.title, item.id) for item in chapter_items]

    # NCX and Nav
    book.add_item(epub.EpubNcx())
    nav = epub.EpubNav()
    book.add_item(nav)

    # Spine
    book.spine = ["nav"] + chapter_items

    # Page list nav (EPUB3 page-list)
    if all_page_ids:
        _add_page_list(book, all_page_ids, metadata.language)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    epub.write_epub(str(output_path), book)
    return output_path


def _add_image(book: epub.EpubBook, img_path: Path, added: set[str]) -> None:
    """Add an image file to the EPUB manifest once, keyed by filename."""
    if img_path.name in added or not img_path.exists():
        return
    media_type = mimetypes.guess_type(img_path.name)[0] or "image/jpeg"
    book.add_item(epub.EpubItem(
        uid=f"img_{img_path.stem}",
        file_name=f"images/{img_path.name}",
        media_type=media_type,
        content=img_path.read_bytes(),
    ))
    added.add(img_path.name)


def _add_page_list(book: epub.EpubBook, page_ids: list[tuple[str, str]], lang: str) -> None:
    """Add an EPUB3 page-list navigation document."""
    items_html = "\n".join(
        f'    <li><a href="{href}">{label}</a></li>'
        for href, label in page_ids
    )
    content = f"""\
<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops"
      xml:lang="{lang}">
<head><title>Page List</title></head>
<body>
  <nav epub:type="page-list" id="page-list">
    <ol>
{items_html}
    </ol>
  </nav>
</body>
</html>"""
    page_list_item = epub.EpubItem(
        uid="page-list",
        file_name="page-list.xhtml",
        media_type="application/xhtml+xml",
        content=content.encode("utf-8"),
    )
    book.add_item(page_list_item)
