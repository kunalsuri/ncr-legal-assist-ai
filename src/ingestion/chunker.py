"""Split KB articles into retrievable chunks at heading boundaries."""
from __future__ import annotations

import re
from pydantic import BaseModel

from src.ingestion.markdown_loader import KBArticle


class Chunk(BaseModel):
    chunk_id: str
    article_id: str
    source_path: str
    heading_path: list[str]
    text: str
    article_status: str
    article_title: str


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def chunk_article(article: KBArticle) -> list[Chunk]:
    """Split on Markdown headings. Each heading section becomes one chunk."""
    chunks: list[Chunk] = []
    sections = _split_by_heading(article.body)
    for i, (heading_path, text) in enumerate(sections):
        if not text.strip():
            continue
        chunks.append(Chunk(
            chunk_id=f"{article.id}#{i:03d}",
            article_id=article.id,
            source_path=article.source_path,
            heading_path=heading_path,
            text=text.strip(),
            article_status=article.status,
            article_title=article.title,
        ))
    return chunks


def _split_by_heading(body: str) -> list[tuple[list[str], str]]:
    """Return [(heading_path, body_text)] pairs."""
    # Simple implementation: split by top-level headings; ignore deeper nesting in v1.
    parts: list[tuple[list[str], str]] = []
    current_heading: list[str] = []
    current_text: list[str] = []
    for line in body.splitlines():
        m = HEADING_RE.match(line)
        if m:
            if current_text:
                parts.append((current_heading, "\n".join(current_text)))
                current_text = []
            current_heading = [m.group(2).strip()]
        else:
            current_text.append(line)
    if current_text:
        parts.append((current_heading, "\n".join(current_text)))
    return parts
