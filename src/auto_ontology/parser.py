"""Deterministic PDF layout extraction with physical page and bbox evidence."""
from __future__ import annotations

import re
import fitz

from .models import ParsedBlock

MAX_BYTES = 15 * 1024 * 1024
MAX_PAGES = 100
MAX_TEXT_BLOCKS = 12000
MAX_EXTRACTED_CHARACTERS = 2_000_000
SECTION_PATTERN = re.compile(r"^\s*(\d+(?:\.\d+){1,6})\s+\S")


class InvalidDocument(ValueError):
    pass


def parse_pdf(data: bytes) -> tuple[int, list[ParsedBlock]]:
    if len(data) > MAX_BYTES:
        raise InvalidDocument("PDF exceeds maximum upload size")
    if not data.lstrip().startswith(b"%PDF-"):
        raise InvalidDocument("File is not a PDF")
    try:
        document = fitz.open(stream=data, filetype="pdf")
        if document.is_encrypted:
            raise InvalidDocument("Encrypted PDFs are not supported")
        if document.page_count == 0:
            raise InvalidDocument("PDF has no pages")
        if document.page_count > MAX_PAGES:
            raise InvalidDocument("PDF exceeds maximum page count")
        results: list[ParsedBlock] = []
        current_section: str | None = None
        total_characters = 0
        for page_index, page in enumerate(document):
            for row in page.get_text("blocks", sort=True):
                if len(row) < 7 or row[6] != 0:
                    continue
                text = str(row[4]).strip()
                total_characters += len(text)
                if total_characters > MAX_EXTRACTED_CHARACTERS:
                    raise InvalidDocument("PDF exceeds maximum extracted text length")
                if not text:
                    continue
                heading = SECTION_PATTERN.match(text.splitlines()[0])
                if heading:
                    current_section = heading.group(1)
                bbox = tuple(round(float(n), 2) for n in row[:4])
                results.append(ParsedBlock(
                    page_no=page_index + 1,
                    block_index=len(results),
                    section_path=current_section,
                    text=text,
                    bbox=bbox,
                ))
                if len(results) > MAX_TEXT_BLOCKS:
                    raise InvalidDocument("PDF exceeds maximum text block count")
        return document.page_count, results
    except InvalidDocument:
        raise
    except (RuntimeError, ValueError, fitz.FileDataError) as exc:
        raise InvalidDocument("PDF is damaged or cannot be parsed") from exc
