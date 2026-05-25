"""Cross-encoder reranker."""
from __future__ import annotations

from FlagEmbedding import FlagReranker


class Reranker:
    def __init__(self, model_name: str) -> None:
        self.model = FlagReranker(model_name, use_fp16=True)

    def score(self, pairs: list[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        scores = self.model.compute_score([list(p) for p in pairs], normalize=True)
        if isinstance(scores, float):
            return [scores]
        return list(scores)
