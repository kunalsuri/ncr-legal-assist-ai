"""BM25 + dense retrieval with reranking and a confidence gate."""
from __future__ import annotations

from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from src.indexing.embeddings import Embedder
from src.indexing.vector_store import VectorStore
from src.retrieval.reranker import Reranker


@dataclass
class RetrievalResult:
    chunk_id: str
    article_id: str
    source_path: str
    heading_path: list[str]
    text: str
    article_status: str
    article_title: str
    rerank_score: float


class HybridRetriever:
    def __init__(
        self,
        vector_store: VectorStore,
        embedder: Embedder,
        reranker: Reranker,
        bm25: BM25Okapi,
        chunks_by_id: dict,
        confidence_threshold: float,
    ) -> None:
        self.vector_store = vector_store
        self.embedder = embedder
        self.reranker = reranker
        self.bm25 = bm25
        self.chunks_by_id = chunks_by_id
        self.confidence_threshold = confidence_threshold

    def retrieve(self, query: str, k: int = 8) -> tuple[list[RetrievalResult], bool]:
        q_vec = self.embedder.encode([query])[0]
        dense_hits = self.vector_store.search(q_vec, limit=k * 3)
        dense_ids = {h["chunk_id"] for h in dense_hits}

        bm25_scores = self.bm25.get_scores(query.lower().split())
        ranked_ids = [cid for cid, _ in sorted(
            zip(self.chunks_by_id.keys(), bm25_scores),
            key=lambda x: -x[1],
        )[: k * 3]]
        candidate_ids = list(dense_ids | set(ranked_ids))

        pairs = [(query, self.chunks_by_id[cid].text) for cid in candidate_ids]
        scores = self.reranker.score(pairs)
        ranked = sorted(zip(candidate_ids, scores), key=lambda x: -x[1])[:k]

        results = [
            RetrievalResult(
                chunk_id=cid,
                article_id=self.chunks_by_id[cid].article_id,
                source_path=self.chunks_by_id[cid].source_path,
                heading_path=self.chunks_by_id[cid].heading_path,
                text=self.chunks_by_id[cid].text,
                article_status=self.chunks_by_id[cid].article_status,
                article_title=self.chunks_by_id[cid].article_title,
                rerank_score=float(score),
            )
            for cid, score in ranked
        ]
        confident = bool(results) and results[0].rerank_score >= self.confidence_threshold
        return results, confident
