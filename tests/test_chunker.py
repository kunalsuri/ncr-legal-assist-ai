"""Tests for src.ingestion.chunker — no external dependencies required."""
from __future__ import annotations

import pytest

from src.ingestion.chunker import Chunk, _split_by_heading, chunk_article
from src.ingestion.markdown_loader import KBArticle


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_article(**overrides: object) -> KBArticle:
    data: dict = {
        "id": "test-art",
        "title": "Test Article",
        "status": "unreviewed-primary-sources-only",
        "jurisdiction": ["Delhi"],
        "topic": "tenancy",
        "audience": "any",
        "language": "en",
        "body": "",
        "source_path": "statutes/test.md",
    }
    data.update(overrides)
    return KBArticle(**data)


# ---------------------------------------------------------------------------
# chunk_article: basic splitting
# ---------------------------------------------------------------------------

class TestChunkArticle:
    def test_empty_body_produces_no_chunks(self) -> None:
        assert chunk_article(_make_article(body="")) == []

    def test_whitespace_body_produces_no_chunks(self) -> None:
        assert chunk_article(_make_article(body="   \n\n  ")) == []

    def test_body_with_no_headings_produces_one_chunk(self) -> None:
        chunks = chunk_article(_make_article(body="Some text without headings."))
        assert len(chunks) == 1
        assert chunks[0].text == "Some text without headings."

    def test_two_headings_produce_two_chunks(self) -> None:
        body = "## Section One\nText one.\n\n## Section Two\nText two."
        chunks = chunk_article(_make_article(body=body))
        assert len(chunks) == 2

    def test_whitespace_only_sections_are_skipped(self) -> None:
        body = "## Empty\n   \n## Real\nContent here."
        chunks = chunk_article(_make_article(body=body))
        assert all(c.text.strip() for c in chunks)

    def test_chunk_text_strips_whitespace(self) -> None:
        body = "## Section\n\n  Content here.  \n\n"
        chunks = chunk_article(_make_article(body=body))
        assert chunks[0].text == "Content here."


# ---------------------------------------------------------------------------
# chunk_article: chunk_id format
# ---------------------------------------------------------------------------

class TestChunkId:
    def test_chunk_id_contains_article_id(self) -> None:
        chunks = chunk_article(_make_article(body="Some content."))
        assert all(c.chunk_id.startswith("test-art#") for c in chunks)

    def test_chunk_id_is_zero_padded(self) -> None:
        body = "## A\nOne.\n## B\nTwo."
        chunks = chunk_article(_make_article(body=body))
        assert chunks[0].chunk_id == "test-art#000"
        assert chunks[1].chunk_id == "test-art#001"

    def test_chunk_id_unique_per_chunk(self) -> None:
        body = "## A\nOne.\n## B\nTwo.\n## C\nThree."
        chunks = chunk_article(_make_article(body=body))
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# chunk_article: inherited metadata
# ---------------------------------------------------------------------------

class TestChunkMetadataInheritance:
    def test_article_id_inherited(self) -> None:
        chunks = chunk_article(_make_article(id="dl-tenancy-deposit", body="Body text here."))
        assert all(c.article_id == "dl-tenancy-deposit" for c in chunks)

    def test_source_path_inherited(self) -> None:
        chunks = chunk_article(_make_article(body="Body text here."))
        assert all(c.source_path == "statutes/test.md" for c in chunks)

    def test_article_status_inherited(self) -> None:
        chunks = chunk_article(_make_article(body="Body text here."))
        assert all(c.article_status == "unreviewed-primary-sources-only" for c in chunks)

    def test_article_title_inherited(self) -> None:
        chunks = chunk_article(_make_article(title="My Title", body="Body text here."))
        assert all(c.article_title == "My Title" for c in chunks)

    def test_heading_path_captured(self) -> None:
        body = "## My Section\nContent here."
        chunks = chunk_article(_make_article(body=body))
        assert any("My Section" in c.heading_path for c in chunks)

    def test_chunk_is_pydantic_model(self) -> None:
        chunks = chunk_article(_make_article(body="Text."))
        assert all(isinstance(c, Chunk) for c in chunks)


# ---------------------------------------------------------------------------
# _split_by_heading: internal helper
# ---------------------------------------------------------------------------

class TestSplitByHeading:
    def test_plain_text_returns_single_part(self) -> None:
        parts = _split_by_heading("plain text")
        assert len(parts) == 1
        assert parts[0][1].strip() == "plain text"

    def test_heading_captures_title_in_path(self) -> None:
        parts = _split_by_heading("## Introduction\nSome text.")
        assert any("Introduction" in path for path, _ in parts)

    def test_two_headings_produce_two_parts(self) -> None:
        parts = _split_by_heading("## A\nText A.\n## B\nText B.")
        assert len(parts) == 2

    def test_text_before_first_heading_captured(self) -> None:
        parts = _split_by_heading("Preamble text.\n## Section\nSection text.")
        texts = [t for _, t in parts]
        assert any("Preamble" in t for t in texts)
