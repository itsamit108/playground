import os
from pathlib import Path

from google import genai
from google.genai import types
from lxml import etree

from domain.models import Chapter, GeneratedChapter

MODEL = "gemini-3.1-flash-lite"
MAX_PAGES_PER_CALL = 8  # stay within Gemini image limits

SYSTEM_INSTRUCTION = """You are a professional EPUB3 content author.

Convert the provided PDF page content into valid XHTML5 for EPUB3.
You will receive:
1. The extracted text/markdown for each page in the chapter
2. A screenshot of each page so you can see the visual layout precisely

Rules:
- Use <h1> for chapter titles, <h2> for section headings, <h3> for sub-sections
- Use <math xmlns="http://www.w3.org/1998/Math/MathML"> for ALL mathematical expressions — convert every equation, formula, fraction, superscript, subscript into proper MathML
- Use <table> with <thead> and <tbody> for any tabular data
- Use <aside class="note"> for definition boxes, notes, callout boxes, and highlighted text
- Use <figure><img src="images/PLACEHOLDER.jpg" alt="description"/><figcaption>caption text</figcaption></figure> for diagrams, charts, and illustrations — describe the image in the alt attribute
- Use <section class="exercise"> wrapping <ol> with <li> items for numbered exercise questions
- Use <blockquote class="epigraph"> for chapter-opening quotes with attribution in <cite>
- Use <p class="example-label"> for "Example N" labels followed by <p class="example-body"> for the content
- Use <p class="solution"> for solution blocks
- Insert <span epub:type="pagebreak" id="page-N" title="N"/> at the start of content from page N
- For any list with items labeled (i), (ii), (iii)... or (a), (b), (c)... or 1., 2., 3.— use <ol><li> not <p> tags
- Each image in the page screenshots is saved as a file. Reference them with <img src="../images/FILENAME" alt="description"/> where FILENAME matches the image filename from the page (e.g. page_1_image_1_v2.jpg). Use the screenshot to identify what each image shows.
- Preserve ALL text content — do not summarise, omit, or paraphrase
- Return ONLY the XHTML body content — no <html>, <head>, or <body> wrapper tags
- The output must be well-formed XML (self-close void elements: <br/>, <hr/>, <img/>)
"""


def generate_chapter_xhtml(chapter: Chapter) -> GeneratedChapter:
    """
    Call Gemini 3.5 Flash with chapter markdown + page screenshots → XHTML body fragment.
    Splits large chapters into batches of MAX_PAGES_PER_CALL pages.
    """
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    all_xhtml_parts: list[str] = []

    pages = chapter.pages
    batches = [pages[i:i + MAX_PAGES_PER_CALL] for i in range(0, len(pages), MAX_PAGES_PER_CALL)]

    for batch in batches:
        xhtml_part = _call_gemini(client, batch)
        all_xhtml_parts.append(xhtml_part)

    combined_xhtml = "\n".join(all_xhtml_parts)
    return GeneratedChapter(chapter=chapter, xhtml=combined_xhtml)


def _call_gemini(client: genai.Client, pages) -> str:
    text_parts = []
    image_parts = []

    for page in pages:
        text_parts.append(
            f"--- PAGE {page.page_number} ---\n{page.markdown}\n"
        )
        if page.screenshot_path and Path(page.screenshot_path).exists():
            img_bytes = Path(page.screenshot_path).read_bytes()
            image_parts.append(
                types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
            )

    # Interleave: all text first, then images (Gemini handles this well)
    content_parts = [types.Part.from_text(text="\n".join(text_parts))] + image_parts

    response = client.models.generate_content(
        model=MODEL,
        contents=[types.Content(role="user", parts=content_parts)],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.1,
            max_output_tokens=65536,
        ),
    )

    raw = response.text or ""
    return _clean_and_validate(raw)


def _clean_and_validate(raw: str) -> str:
    """
    Strip markdown code fences if Gemini wrapped the output, then validate XML.
    Falls back to returning escaped plain text if XML is broken.
    """
    # Strip ```xml ... ``` or ```html ... ``` fences
    if raw.startswith("```"):
        lines = raw.splitlines()
        # Drop first and last fence lines
        inner = lines[1:] if lines[0].startswith("```") else lines
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        raw = "\n".join(inner)

    # Validate by wrapping in a root element and parsing
    wrapped = f"<root xmlns:epub='http://www.idpf.org/2007/ops'>{raw}</root>"
    try:
        etree.fromstring(wrapped.encode("utf-8"))
        return raw
    except etree.XMLSyntaxError:
        # Return as a preformatted fallback — at least the text is preserved
        escaped = raw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"<pre>{escaped}</pre>"
