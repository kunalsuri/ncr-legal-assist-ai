"""Ollama integration: status check, model listing, and OpenAI-compatible generation."""
from __future__ import annotations

from collections.abc import Generator
from typing import Any

import httpx
from openai import OpenAI

OLLAMA_BASE_URL = "http://localhost:11434"


def is_ollama_running(base_url: str = OLLAMA_BASE_URL, timeout: float = 2.0) -> bool:
    """Return True if the Ollama server is reachable."""
    try:
        r = httpx.get(f"{base_url}/api/tags", timeout=timeout)
        return r.status_code == 200
    except httpx.RequestError:
        return False


def list_ollama_models(base_url: str = OLLAMA_BASE_URL, timeout: float = 5.0) -> list[str]:
    """Return a sorted list of local Ollama model names."""
    try:
        r = httpx.get(f"{base_url}/api/tags", timeout=timeout)
        r.raise_for_status()
        data = r.json()
        return sorted(m["name"] for m in data.get("models", []))
    except (httpx.RequestError, httpx.HTTPStatusError, KeyError, ValueError):
        return []


class OllamaLLMClient:
    """LLM client that targets Ollama's OpenAI-compatible `/v1` endpoint."""

    def __init__(
        self,
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 1024,
        base_url: str = OLLAMA_BASE_URL,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        # Ollama's OpenAI-compatible endpoint; api_key value is ignored by Ollama
        self._client = OpenAI(base_url=f"{base_url}/v1", api_key="ollama")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or ""

    def generate_stream(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> Generator[str, None, None]:
        """Stream response tokens for a multi-turn conversation.

        ``messages`` is the full conversation history in OpenAI format
        (each dict has ``role`` and ``content``).  The system prompt is
        prepended automatically and must *not* appear in ``messages``.
        """
        full_messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ] + messages
        stream: Any = self._client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=full_messages,  # type: ignore[arg-type]
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
