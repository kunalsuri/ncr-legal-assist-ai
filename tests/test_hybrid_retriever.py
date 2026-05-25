"""Tests for HybridRetriever — all ML dependencies are mocked, no models loaded."""
from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest

from src.ingestion.chunker import Chunk
from src.retrieval.hybrid_retriever import HybridRetriever, RetrievalResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(chunk_id: str, article_id: str = "art-a") -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        article_id=article_id,
        source_path="statutes/test.md",
        heading_path=["Section"],
        text=f"Text for {chunk_id}.",
        article_status="unreviewed-primary-sources-only",
        article_title="Test Article",
    )


def _make_retriever(
    chunks: dict[str, Chunk],
    dense_hits: list[dict],
    rerank_score: float = 0.9,
    threshold: float = 0.5,
) -> HybridRetriever:
    """Build a HybridRetriever with all external collaborators mocked."""
    mock_embedder = MagicMock()
    mock_embedder.encode.return_value = np.array([[0.1, 0.2, 0.3]])

    mock_vs = MagicMock()
    mock_vs.search.return_value = dense_hits

    mock_reranker = MagicMock()
    # Return one score per pair so the scorer never mismatches candidate count
    mock_reranker.score.side_effect = lambda pairs: [rerank_score] * len(pairs)

    # BM25 scores: one score per chunk, all equal so order is deterministic
    mock_bm25 = MagicMock()
    mock_bm25.get_scores.return_value = np.array([0.5] * len(chunks))

    return HybridRetriever(
        vector_store=mock_vs,
        embedder=mock_embedder,
        reranker=mock_reranker,
        bm25=mock_bm25,
        chunks_by_id=chunks,
        confidence_threshold=threshold,
    )


# ---------------------------------------------------------------------------
# HybridRetriever.retrieve
# ---------------------------------------------------------------------------

class TestHybridRetrieverRetrieve:
    def test_confident_when_top_score_above_threshold(self) -> None:
        chunk = _make_chunk("art-a#000")
        retriever = _make_retriever(
            chunks={"art-a#000": chunk},
            dense_hits=[{"chunk_id": "art-a#000", "score": 0.9}],
            rerank_score=0.9,
            threshold=0.5,
        )
        results, confident = retriever.retrieve("security deposit", k=1)
        assert confident is True
        assert len(results) >= 1

    def test_not_confident_when_top_score_below_threshold(self) -> None:
        chunk = _make_chunk("art-a#000")
        retriever = _make_retriever(
            chunks={"art-a#000": chunk},
            dense_hits=[{"chunk_id": "art-a#000", "score": 0.3}],
            rerank_score=0.3,
            threshold=0.5,
        )
        _, confident = retriever.retrieve("deposit refund", k=1)
        assert confident is False

    def test_empty_store_returns_empty_results_and_not_confident(self) -> None:
        retriever = _make_retriever(chunks={}, dense_hits=[], threshold=0.5)
        results, confident = retriever.retrieve("anything", k=5)
        assert results == []
        assert confident is False

    def test_result_fields_populated_correctly(self) -> None:
        chunk = _make_chunk("art-a#000", article_id="my-article")
        retriever = _make_retriever(
            chunks={"art-a#000": chunk},
            dense_hits=[{"chunk_id": "art-a#000", "score": 0.9}],
            rerank_score=0.9,
            threshold=0.5,
        )
        results, _ = retriever.retrieve("query", k=1)
        r = results[0]
        assert r.chunk_id == "art-a#000"
        assert r.article_id == "my-article"
        assert r.source_path == "statutes/test.md"
        assert r.article_status == "unreviewed-primary-sources-only"
        assert isinstance(r.rerank_score, float)

    def test_results_are_retrieval_result_instances(self) -> None:
        chunk = _make_chunk("art-a#000")
        retriever = _make_retriever(
            chunks={"art-a#000": chunk},
            dense_hits=[{"chunk_id": "art-a#000", "score": 0.9}],
            rerank_score=0.9,
        )
        results, _ = retriever.retrieve("query", k=1)
        assert all(isinstance(r, RetrievalResult) for r in results)

    def test_k_limits_number_of_results(self) -> None:
        chunks = {f"art-a#{i:03d}": _make_chunk(f"art-a#{i:03d}") for i in range(5)}
        dense_hits = [{"chunk_id": cid, "score": 0.9} for cid in chunks]
        retriever = _make_retriever(
            chunks=chunks,
            dense_hits=dense_hits,
            rerank_score=0.9,
            threshold=0.5,
        )
        results, _ = retriever.retrieve("query", k=2)
        assert len(results) <= 2

    def test_confidence_exactly_at_threshold_is_confident(self) -> None:
        chunk = _make_chunk("art-a#000")
        retriever = _make_retriever(
            chunks={"art-a#000": chunk},
            dense_hits=[{"chunk_id": "art-a#000", "score": 0.5}],
            rerank_score=0.5,
            threshold=0.5,
        )
        _, confident = retriever.retrieve("query", k=1)
        assert confident is True
