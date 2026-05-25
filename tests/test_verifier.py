"""Tests for src.generation.verifier — the citation-integrity gate."""
from __future__ import annotations

from src.generation.verifier import CITATION_PATTERN, verify_answer


# ---------------------------------------------------------------------------
# verify_answer: basic cases
# ---------------------------------------------------------------------------

class TestVerifyAnswerBasic:
    def test_valid_citation(self) -> None:
        ok, fab = verify_answer(
            "The Act says X [dl-tenancy-deposit-recovery, S.27].",
            {"dl-tenancy-deposit-recovery"},
        )
        assert ok and fab == []

    def test_fabricated_citation(self) -> None:
        ok, fab = verify_answer("The Act says X [fake-article-id, S.99].", set())
        assert not ok
        assert fab == ["fake-article-id"]

    def test_no_citation_fails(self) -> None:
        ok, fab = verify_answer("The Act says X.", {"dl-tenancy-deposit-recovery"})
        assert not ok
        assert fab == []

    def test_empty_answer_fails(self) -> None:
        ok, fab = verify_answer("", set())
        assert not ok
        assert fab == []

    def test_empty_answer_with_retrieved_sources_fails(self) -> None:
        ok, fab = verify_answer("", {"dl-tenancy-deposit-recovery"})
        assert not ok

    def test_cited_id_absent_from_retrieved_is_fabricated(self) -> None:
        ok, fab = verify_answer("See [real-id, §1].", {"other-id"})
        assert not ok
        assert "real-id" in fab


# ---------------------------------------------------------------------------
# verify_answer: multiple citations
# ---------------------------------------------------------------------------

class TestVerifyAnswerMultipleCitations:
    def test_all_valid_citations_pass(self) -> None:
        ok, fab = verify_answer(
            "See [art-a, §1] and [art-b, §2].",
            {"art-a", "art-b"},
        )
        assert ok and fab == []

    def test_mixed_citations_fails_and_lists_fabricated(self) -> None:
        ok, fab = verify_answer(
            "See [art-a, §1] and [fake-id, §2].",
            {"art-a"},
        )
        assert not ok
        assert "fake-id" in fab
        assert "art-a" not in fab

    def test_multiple_fabricated_ids_all_listed(self) -> None:
        ok, fab = verify_answer(
            "See [fake-1, §1] and [fake-2, §2].",
            set(),
        )
        assert not ok
        assert sorted(fab) == ["fake-1", "fake-2"]

    def test_fabricated_ids_returned_sorted(self) -> None:
        ok, fab = verify_answer(
            "[z-article, §1] and [a-article, §2].",
            set(),
        )
        assert fab == ["a-article", "z-article"]

    def test_same_id_cited_twice_counts_once(self) -> None:
        ok, fab = verify_answer(
            "[art-a, §1] and [art-a, §2].",
            {"art-a"},
        )
        assert ok and fab == []


# ---------------------------------------------------------------------------
# CITATION_PATTERN: regex edge cases
# ---------------------------------------------------------------------------

class TestCitationPattern:
    def test_matches_standard_citation(self) -> None:
        m = CITATION_PATTERN.findall("[dl-tenancy-deposit-recovery, S.27]")
        assert m == ["dl-tenancy-deposit-recovery"]

    def test_matches_id_without_section(self) -> None:
        m = CITATION_PATTERN.findall("[dl-some-article, heading text]")
        assert m == ["dl-some-article"]

    def test_does_not_match_uppercase_id(self) -> None:
        # Pattern requires all-lowercase IDs
        m = CITATION_PATTERN.findall("[SomeArticle, §1]")
        assert m == []

    def test_no_brackets_no_match(self) -> None:
        m = CITATION_PATTERN.findall("plain text no citation")
        assert m == []

    def test_multiple_citations_extracted(self) -> None:
        m = CITATION_PATTERN.findall("[art-a, §1] and [art-b, §2]")
        assert set(m) == {"art-a", "art-b"}
