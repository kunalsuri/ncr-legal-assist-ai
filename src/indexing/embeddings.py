"""Wrap an embedding model. v1 uses sentence-transformers with InLegalBERT."""
from __future__ import annotations

from sentence_transformers import SentenceTransformer
import numpy as np


class Embedder:
    def __init__(self, model_name: str) -> None:
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True)

    @property
    def dim(self) -> int:
        return self.model.get_sentence_embedding_dimension()
