"""Configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    # Ollama settings (used when OLLAMA_BASE_URL is set or as default backend)
    ollama_base_url: str
    # LLM settings — default to Ollama's OpenAI-compatible endpoint
    llm_endpoint: str
    llm_model: str  # empty string means "let the user pick in the UI"
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
    ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return Config(
        ollama_base_url=ollama_base,
        # Default LLM endpoint to Ollama; override with LLM_ENDPOINT env var
        llm_endpoint=os.getenv("LLM_ENDPOINT", f"{ollama_base}/v1"),
        # Empty default so the Streamlit sidebar model picker takes precedence
        llm_model=os.getenv("LLM_MODEL", ""),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
        embedding_model=os.getenv("EMBEDDING_MODEL", "law-ai/InLegalBERT"),
        reranker_model=os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3"),
        qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
        qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
        qdrant_collection=os.getenv("QDRANT_COLLECTION", "delhi_legal_kb"),
        top_k=int(os.getenv("TOP_K", "8")),
        rerank_confidence_threshold=float(
            os.getenv("RERANK_CONFIDENCE_THRESHOLD", "0.55")
        ),
        kb_root=Path(os.getenv("KB_ROOT", "./knowledge_base")),
        data_root=Path(os.getenv("DATA_ROOT", "./data")),
    )
