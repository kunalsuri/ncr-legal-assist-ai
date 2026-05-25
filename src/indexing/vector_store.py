"""Qdrant wrapper for the KB collection."""
from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from src.ingestion.chunker import Chunk


class VectorStore:
    def __init__(self, host: str, port: int, collection: str, dim: int) -> None:
        self.client = QdrantClient(host=host, port=port)
        self.collection = collection
        self._ensure_collection(dim)

    def _ensure_collection(self, dim: int) -> None:
        existing = {c.name for c in self.client.get_collections().collections}
        if self.collection not in existing:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=qm.VectorParams(size=dim, distance=qm.Distance.COSINE),
            )

    def upsert(self, chunks: list[Chunk], vectors) -> None:
        points = [
            qm.PointStruct(
                id=i,
                vector=vec.tolist(),
                payload={
                    "chunk_id": c.chunk_id,
                    "article_id": c.article_id,
                    "source_path": c.source_path,
                    "heading_path": c.heading_path,
                    "text": c.text,
                    "article_status": c.article_status,
                    "article_title": c.article_title,
                },
            )
            for i, (c, vec) in enumerate(zip(chunks, vectors))
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query_vec, limit: int) -> list[dict]:
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=query_vec.tolist(),
            limit=limit,
        )
        return [h.payload | {"score": h.score} for h in hits]
