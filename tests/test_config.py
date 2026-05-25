"""Tests for src.config — environment variable overrides and immutability."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config import Config, load_config


# ---------------------------------------------------------------------------
# load_config: defaults
# ---------------------------------------------------------------------------

class TestLoadConfigDefaults:
    def test_returns_config_instance(self) -> None:
        cfg = load_config()
        assert isinstance(cfg, Config)

    def test_default_ollama_url(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            cfg = load_config()
        assert cfg.ollama_base_url == "http://localhost:11434"

    def test_default_llm_endpoint_uses_ollama_base(self) -> None:
        cfg = load_config()
        assert "11434" in cfg.llm_endpoint or cfg.llm_endpoint.startswith("http")

    def test_default_temperature_is_low(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            cfg = load_config()
        assert cfg.llm_temperature == pytest.approx(0.1)

    def test_default_max_tokens_positive(self) -> None:
        cfg = load_config()
        assert cfg.llm_max_tokens > 0

    def test_default_top_k_positive(self) -> None:
        cfg = load_config()
        assert cfg.top_k > 0

    def test_default_confidence_threshold_in_unit_range(self) -> None:
        cfg = load_config()
        assert 0.0 <= cfg.rerank_confidence_threshold <= 1.0

    def test_kb_root_is_path(self) -> None:
        cfg = load_config()
        assert isinstance(cfg.kb_root, Path)

    def test_data_root_is_path(self) -> None:
        cfg = load_config()
        assert isinstance(cfg.data_root, Path)


# ---------------------------------------------------------------------------
# load_config: environment variable overrides
# ---------------------------------------------------------------------------

class TestLoadConfigEnvOverrides:
    def test_override_ollama_url(self) -> None:
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://remote:9000"}):
            cfg = load_config()
        assert cfg.ollama_base_url == "http://remote:9000"

    def test_override_llm_model(self) -> None:
        with patch.dict(os.environ, {"LLM_MODEL": "mistral:7b"}):
            cfg = load_config()
        assert cfg.llm_model == "mistral:7b"

    def test_override_temperature(self) -> None:
        with patch.dict(os.environ, {"LLM_TEMPERATURE": "0.9"}):
            cfg = load_config()
        assert cfg.llm_temperature == pytest.approx(0.9)

    def test_override_max_tokens(self) -> None:
        with patch.dict(os.environ, {"LLM_MAX_TOKENS": "2048"}):
            cfg = load_config()
        assert cfg.llm_max_tokens == 2048

    def test_override_top_k(self) -> None:
        with patch.dict(os.environ, {"TOP_K": "5"}):
            cfg = load_config()
        assert cfg.top_k == 5

    def test_override_confidence_threshold(self) -> None:
        with patch.dict(os.environ, {"RERANK_CONFIDENCE_THRESHOLD": "0.75"}):
            cfg = load_config()
        assert cfg.rerank_confidence_threshold == pytest.approx(0.75)

    def test_override_qdrant_port(self) -> None:
        with patch.dict(os.environ, {"QDRANT_PORT": "6334"}):
            cfg = load_config()
        assert cfg.qdrant_port == 6334

    def test_override_kb_root(self) -> None:
        with patch.dict(os.environ, {"KB_ROOT": "/tmp/kb"}):
            cfg = load_config()
        assert cfg.kb_root == Path("/tmp/kb")


# ---------------------------------------------------------------------------
# Config: immutability (frozen dataclass)
# ---------------------------------------------------------------------------

class TestConfigImmutability:
    def test_config_is_frozen(self) -> None:
        cfg = load_config()
        with pytest.raises((AttributeError, TypeError)):
            cfg.llm_model = "hack"  # type: ignore[misc]

    def test_config_fields_accessible(self) -> None:
        cfg = load_config()
        # All fields accessible without raising
        _ = cfg.ollama_base_url
        _ = cfg.llm_endpoint
        _ = cfg.llm_model
        _ = cfg.llm_temperature
        _ = cfg.llm_max_tokens
        _ = cfg.embedding_model
        _ = cfg.reranker_model
        _ = cfg.qdrant_host
        _ = cfg.qdrant_port
        _ = cfg.qdrant_collection
        _ = cfg.top_k
        _ = cfg.rerank_confidence_threshold
        _ = cfg.kb_root
        _ = cfg.data_root
