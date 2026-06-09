from dataclasses import dataclass, field


@dataclass
class ParsedPage:
    page_number: int
    markdown: str
    screenshot_path: str              # local path to page_N.jpg from LlamaParse
    embedded_image_paths: list[str] = field(default_factory=list)  # local paths to embedded/layout images


@dataclass
class Chapter:
    index: int
    title: str
    pages: list[ParsedPage] = field(default_factory=list)


@dataclass
class BookMetadata:
    title: str
    author: str
    language: str = "en"
    subject: str = ""
    identifier: str = ""


@dataclass
class GeneratedChapter:
    chapter: Chapter
    xhtml: str  # complete XHTML body fragment
