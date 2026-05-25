"""Tests for src.ingestion.markdown_loader — runs without network access."""
from __future__ import annotations

from pathlib import Path
import tempfile

import pytest
from pydantic import ValidationError

from src.ingestion.markdown_loader import KBArticle, load_kb

# ---------------------------------------------------------------------------
# Reusable fixtures
# ---------------------------------------------------------------------------

VALID_FM = (
    "---\n"
    "id: test-article\n"
    "title: Test Article\n"
    "status: unreviewed-primary-sources-only\n"
    "jurisdiction: [Delhi]\n"
    "topic: tenancy\n"
    "audience: any\n"
    "language: en\n"
    "---\n\n"
    "Some body text with a citation [TPA §106]."
)

REVIEWED_FM = (
    "---\n"
    "id: test-reviewed\n"
    "title: Reviewed Article\n"
    "status: reviewed\n"
    "jurisdiction: [Delhi]\n"
    "topic: property\n"
    "audience: buyer\n"
    "language: en\n"
    "reviewer: Jane Doe\n"
    "last_reviewed: '2026-01-15'\n"
    "disclaimer_level: standard\n"
    "---\n\n"
    "Body text [Registration Act §17]."
)

DEPRECATED_FM = (
    "---\n"
    "id: test-deprecated\n"
    "title: Deprecated Article\n"
    "status: deprecated\n"
    "jurisdiction: [Delhi]\n"
    "topic: tenancy\n"
    "audience: any\n"
    "language: en\n"
    "---\n\n"
    "Old content [DRCA §5]."
)


def _write(tmp: str, name: str, content: str) -> Path:
    p = Path(tmp) / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# load_kb: skipping behaviour
# ---------------------------------------------------------------------------

class TestLoadKbSkipping:
    def test_empty_template_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(
                tmp, "empty.md",
                "---\nid: x\ntitle: x\nstatus: unreviewed-primary-sources-only\n"
                "jurisdiction: [Delhi]\ntopic: tenancy\naudience: any\n"
                "language: en\n---\n\n<!-- TODO -->",
            )
            assert load_kb(Path(tmp)) == []

    def test_whitespace_only_body_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(
                tmp, "blank.md",
                "---\nid: x\ntitle: x\nstatus: unreviewed-primary-sources-only\n"
                "jurisdiction: [Delhi]\ntopic: tenancy\naudience: any\n"
                "language: en\n---\n\n   \n\n",
            )
            assert load_kb(Path(tmp)) == []

    def test_readme_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(tmp, "README.md", VALID_FM)
            assert load_kb(Path(tmp)) == []

    def test_schema_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(tmp, "SCHEMA.md", VALID_FM)
            assert load_kb(Path(tmp)) == []


# ---------------------------------------------------------------------------
# load_kb: loading behaviour
# ---------------------------------------------------------------------------

class TestLoadKbLoading:
    def test_valid_article_loads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(tmp, "article.md", VALID_FM)
            articles = load_kb(Path(tmp))
            assert len(articles) == 1
            a = articles[0]
            assert a.id == "test-article"
            assert a.title == "Test Article"
            assert a.status == "unreviewed-primary-sources-only"
            assert a.jurisdiction == ["Delhi"]
            assert a.topic == "tenancy"
            assert "citation" in a.body

    def test_reviewed_status_loads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(tmp, "reviewed.md", REVIEWED_FM)
            articles = load_kb(Path(tmp))
            assert len(articles) == 1
            assert articles[0].status == "reviewed"

    def test_deprecated_status_loads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(tmp, "depr.md", DEPRECATED_FM)
            articles = load_kb(Path(tmp))
            assert len(articles) == 1
            assert articles[0].status == "deprecated"

    def test_multiple_articles_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(tmp, "a.md", VALID_FM)
            _write(tmp, "b.md", REVIEWED_FM)
            articles = load_kb(Path(tmp))
            assert len(articles) == 2
            assert {a.id for a in articles} == {"test-article", "test-reviewed"}

    def test_nested_articles_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp) / "statutes"
            sub.mkdir()
            (sub / "nested.md").write_text(VALID_FM, encoding="utf-8")
            articles = load_kb(Path(tmp))
            assert len(articles) == 1

    def test_source_path_is_relative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write(tmp, "article.md", VALID_FM)
            articles = load_kb(Path(tmp))
            assert not Path(articles[0].source_path).is_absolute()

    def test_missing_required_field_raises(self) -> None:
        # Frontmatter missing status / jurisdiction / topic / audience / language
        bad = "---\nid: x\ntitle: x\n---\n\nSome body."
        with tempfile.TemporaryDirectory() as tmp:
            _write(tmp, "bad.md", bad)
            with pytest.raises((ValidationError, Exception)):
                load_kb(Path(tmp))


# ---------------------------------------------------------------------------
# KBArticle model: validation
# ---------------------------------------------------------------------------

class TestKBArticleModel:
    def _base(self, **overrides: object) -> dict:
        data: dict = {
            "id": "test-id",
            "title": "Title",
            "status": "unreviewed-primary-sources-only",
            "jurisdiction": ["Delhi"],
            "topic": "tenancy",
            "audience": "any",
            "language": "en",
            "body": "Body text.",
            "source_path": "statutes/test.md",
        }
        data.update(overrides)
        return data

    def test_valid_article_constructs(self) -> None:
        a = KBArticle(**self._base())
        assert a.id == "test-id"
        assert a.disclaimer_level == "high"
        assert a.primary_sources == []

    def test_defaults_are_correct(self) -> None:
        a = KBArticle(**self._base())
        assert a.primary_sources == []
        assert a.secondary_sources_consulted == []
        assert a.last_reviewed is None
        assert a.reviewer is None
        assert a.disclaimer_level == "high"

    def test_invalid_status_raises(self) -> None:
        with pytest.raises(ValidationError):
            KBArticle(**self._base(status="nonsense"))

    def test_invalid_language_raises(self) -> None:
        with pytest.raises(ValidationError):
            KBArticle(**self._base(language="fr"))

    def test_invalid_disclaimer_level_raises(self) -> None:
        with pytest.raises(ValidationError):
            KBArticle(**self._base(disclaimer_level="medium"))

    def test_standard_disclaimer_level_accepted(self) -> None:
        a = KBArticle(**self._base(disclaimer_level="standard"))
        assert a.disclaimer_level == "standard"

    def test_hindi_language_accepted(self) -> None:
        a = KBArticle(**self._base(language="hi"))
        assert a.language == "hi"
