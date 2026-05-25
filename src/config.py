"""Configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    llm_endpoint: str
    llm_model: str
    llm_temperature: float
    llm_max_tokens: int
    embedding_model: str
    reranker_model: str
    qdrant_host: str
    qdrant_port: int
    qdrant_collection: str
    top_k: int
    rerank_confidence_threshold: float
    kb_root: Path
    data_root: Path


def load_config() -> Config:
    return Config(
        llm_endpoint=os.environ["LLM_ENDPOINT"],
        llm_model=os.environ["LLM_MODEL"],
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
        embedding_model=os.environ["EMBEDDING_MODEL"],
        reranker_model=os.environ["RERANKER_MODEL"],
        qdrant_host=os.environ["QDRANT_HOST"],
        qdrant_port=int(os.environ["QDRANT_PORT"]),
        qdrant_collection=os.environ["QDRANT_COLLECTION"],
        top_k=int(os.getenv("TOP_K", "8")),
        rerank_confidence_threshold=float(
            os.getenv("RERANK_CONFIDENCE_THRESHOLD", "0.55")
        ),
        kb_root=Path(os.environ["KB_ROOT"]),
        data_root=Path(os.environ["DATA_ROOT"]),
    )
