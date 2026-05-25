"""Build the BM25 and dense indexes from the knowledge base."""
from __future__ import annotations

import pickle
from pathlib import Path

from rank_bm25 import BM25Okapi

from src.config import load_config
from src.indexing.embeddings import Embedder
from src.indexing.vector_store import VectorStore
from src.ingestion.chunker import chunk_article
from src.ingestion.markdown_loader import load_kb


def main() -> None:
    cfg = load_config()
    articles = load_kb(cfg.kb_root)
    print(f"Loaded {len(articles)} non-empty KB articles.")

    if not articles:
        print("Knowledge base is empty. Nothing to index. "
              "Author articles under knowledge_base/statutes/ and rerun.")
        return

    chunks = [c for a in articles for c in chunk_article(a)]
    print(f"Chunked into {len(chunks)} pieces.")

    embedder = Embedder(cfg.embedding_model)
    vectors = embedder.encode([c.text for c in chunks])

    vs = VectorStore(cfg.qdrant_host, cfg.qdrant_port, cfg.qdrant_collection, embedder.dim)
    vs.upsert(chunks, vectors)

    bm25 = BM25Okapi([c.text.lower().split() for c in chunks])
    cfg.data_root.mkdir(parents=True, exist_ok=True)
    with open(cfg.data_root / "bm25.pkl", "wb") as f:
        pickle.dump({"bm25": bm25, "chunks": chunks}, f)

    print("Index built.")


if __name__ == "__main__":
    main()
