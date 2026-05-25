"""Load Markdown KB files with YAML frontmatter into typed records."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import frontmatter
from pydantic import BaseModel, Field


class PrimarySource(BaseModel):
    act: str
    sections: list[str]
    url: str


class KBArticle(BaseModel):
    id: str
    title: str
    status: Literal["unreviewed-primary-sources-only", "reviewed", "deprecated"]
    jurisdiction: list[str]
    topic: str
    audience: str
    language: Literal["en", "hi"]
    primary_sources: list[PrimarySource] = Field(default_factory=list)
    secondary_sources_consulted: list[str] = Field(default_factory=list)
    last_reviewed: str | None = None
    reviewer: str | None = None
    disclaimer_level: Literal["high", "standard"] = "high"
    body: str
    source_path: str


def load_kb(kb_root: Path) -> list[KBArticle]:
    """Walk kb_root and return all valid articles. Skip files with empty bodies."""
    articles: list[KBArticle] = []
    for md_path in kb_root.rglob("*.md"):
        if md_path.name in {"README.md", "SCHEMA.md"}:
            continue
        post = frontmatter.load(md_path)
        if not post.content.strip() or post.content.strip().startswith("<!--"):
            continue  # skip empty template files
        article = KBArticle(
            **post.metadata,
            body=post.content,
            source_path=str(md_path.relative_to(kb_root)),
        )
        articles.append(article)
    return articles
