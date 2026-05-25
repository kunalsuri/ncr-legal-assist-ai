"""Tests for src.generation.prompts — refusal, system prompt, and formatting invariants."""
from __future__ import annotations

from src.generation.prompts import REFUSAL_MESSAGE, SYSTEM_PROMPT, USER_TEMPLATE, format_sources


# ---------------------------------------------------------------------------
# REFUSAL_MESSAGE
# ---------------------------------------------------------------------------

class TestRefusalMessage:
    def test_mentions_dslsa_helpline(self) -> None:
        assert "1516" in REFUSAL_MESSAGE

    def test_mentions_nyaaya(self) -> None:
        assert "Nyaaya" in REFUSAL_MESSAGE

    def test_mentions_nyaaya_url(self) -> None:
        assert "nyaaya.org" in REFUSAL_MESSAGE

    def test_not_empty(self) -> None:
        assert REFUSAL_MESSAGE.strip()

    def test_does_not_give_direct_legal_advice(self) -> None:
        lowered = REFUSAL_MESSAGE.lower()
        assert "you should" not in lowered
        assert "you must" not in lowered


# ---------------------------------------------------------------------------
# SYSTEM_PROMPT
# ---------------------------------------------------------------------------

class TestSystemPrompt:
    def test_not_empty(self) -> None:
        assert SYSTEM_PROMPT.strip()

    def test_instructs_cite_or_refuse(self) -> None:
        assert "citation" in SYSTEM_PROMPT.lower() or "cite" in SYSTEM_PROMPT.lower()

    def test_instructs_answer_from_sources_only(self) -> None:
        assert "sources" in SYSTEM_PROMPT.lower()

    def test_contains_unreviewed_handling_rule(self) -> None:
        assert "unreviewed" in SYSTEM_PROMPT.lower()

    def test_not_a_lawyer_disclaimer_present(self) -> None:
        lowered = SYSTEM_PROMPT.lower()
        assert "not a lawyer" in lowered or "not give legal advice" in lowered

    def test_refusal_phrase_instructs_helpline(self) -> None:
        assert "1516" in SYSTEM_PROMPT

    def test_contains_format_instruction(self) -> None:
        # Must specify the citation format [article_id, heading]
        assert "article_id" in SYSTEM_PROMPT or "[" in SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# USER_TEMPLATE
# ---------------------------------------------------------------------------

class TestUserTemplate:
    def test_has_query_placeholder(self) -> None:
        assert "{query}" in USER_TEMPLATE

    def test_has_sources_placeholder(self) -> None:
        assert "{formatted_sources}" in USER_TEMPLATE

    def test_formats_correctly(self) -> None:
        filled = USER_TEMPLATE.format(query="What is TPA?", formatted_sources="source text")
        assert "What is TPA?" in filled
        assert "source text" in filled


# ---------------------------------------------------------------------------
# format_sources
# ---------------------------------------------------------------------------

def _mock_result(
    article_id: str = "art-a",
    text: str = "Some text.",
    heading_path: list[str] | None = None,
    article_status: str = "unreviewed-primary-sources-only",
    source_path: str = "statutes/test.md",
) -> object:
    return type("R", (), {
        "article_id": article_id,
        "article_status": article_status,
        "source_path": source_path,
        "heading_path": heading_path if heading_path is not None else [],
        "text": text,
    })()


class TestFormatSources:
    def test_empty_list_returns_empty_string(self) -> None:
        assert format_sources([]) == ""

    def test_single_result_contains_article_id(self) -> None:
        output = format_sources([_mock_result(article_id="dl-tenancy-deposit-recovery")])
        assert "dl-tenancy-deposit-recovery" in output

    def test_single_result_contains_text(self) -> None:
        output = format_sources([_mock_result(text="Statutory text here.")])
        assert "Statutory text here." in output

    def test_single_result_contains_status(self) -> None:
        output = format_sources([_mock_result()])
        assert "unreviewed-primary-sources-only" in output

    def test_heading_path_rendered(self) -> None:
        output = format_sources([_mock_result(heading_path=["Section One"])])
        assert "Section One" in output

    def test_empty_heading_path_shows_top(self) -> None:
        output = format_sources([_mock_result(heading_path=[])])
        assert "(top)" in output

    def test_multiple_results_separated_by_divider(self) -> None:
        output = format_sources([
            _mock_result(article_id="art-a", text="Text A."),
            _mock_result(article_id="art-b", text="Text B."),
        ])
        assert "Text A." in output
        assert "Text B." in output
        assert "---" in output
