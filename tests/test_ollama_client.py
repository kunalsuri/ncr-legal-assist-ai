"""Tests for OllamaLLMClient — all network calls are mocked, no server required."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.generation.ollama_client import OllamaLLMClient, is_ollama_running, list_ollama_models


# ---------------------------------------------------------------------------
# is_ollama_running
# ---------------------------------------------------------------------------

class TestIsOllamaRunning:
    def test_returns_true_when_server_responds_200(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("src.generation.ollama_client.httpx.get", return_value=mock_resp):
            assert is_ollama_running() is True

    def test_returns_false_on_request_error(self) -> None:
        with patch(
            "src.generation.ollama_client.httpx.get",
            side_effect=httpx.RequestError("no server"),
        ):
            assert is_ollama_running() is False

    def test_returns_false_on_non_200_status(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        with patch("src.generation.ollama_client.httpx.get", return_value=mock_resp):
            assert is_ollama_running() is False

    def test_custom_base_url_used_in_request(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("src.generation.ollama_client.httpx.get", return_value=mock_resp) as m:
            is_ollama_running(base_url="http://custom:9999")
            m.assert_called_once_with("http://custom:9999/api/tags", timeout=2.0)


# ---------------------------------------------------------------------------
# list_ollama_models
# ---------------------------------------------------------------------------

class TestListOllamaModels:
    def test_returns_sorted_model_names(self) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "models": [{"name": "llama3.2"}, {"name": "codellama"}, {"name": "mistral"}]
        }
        with patch("src.generation.ollama_client.httpx.get", return_value=mock_resp):
            models = list_ollama_models()
        assert models == sorted(["llama3.2", "codellama", "mistral"])

    def test_returns_empty_list_on_request_error(self) -> None:
        with patch(
            "src.generation.ollama_client.httpx.get",
            side_effect=httpx.RequestError("down"),
        ):
            assert list_ollama_models() == []

    def test_returns_empty_list_on_http_status_error(self) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=MagicMock()
        )
        with patch("src.generation.ollama_client.httpx.get", return_value=mock_resp):
            assert list_ollama_models() == []

    def test_returns_empty_list_when_models_key_absent(self) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        with patch("src.generation.ollama_client.httpx.get", return_value=mock_resp):
            assert list_ollama_models() == []

    def test_single_model_returned(self) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"models": [{"name": "llama3.2"}]}
        with patch("src.generation.ollama_client.httpx.get", return_value=mock_resp):
            assert list_ollama_models() == ["llama3.2"]


# ---------------------------------------------------------------------------
# OllamaLLMClient.generate
# ---------------------------------------------------------------------------

class TestOllamaLLMClientGenerate:
    def test_returns_string_from_model_response(self) -> None:
        with patch("src.generation.ollama_client.OpenAI") as MockOpenAI:
            mock_choice = MagicMock()
            mock_choice.message.content = "Paris is the capital of France."
            MockOpenAI.return_value.chat.completions.create.return_value = MagicMock(
                choices=[mock_choice]
            )
            client = OllamaLLMClient(model="llama3.2")
            result = client.generate("You are helpful.", "Capital of France?")
        assert result == "Paris is the capital of France."
        assert isinstance(result, str)

    def test_returns_empty_string_when_content_is_none(self) -> None:
        with patch("src.generation.ollama_client.OpenAI") as MockOpenAI:
            mock_choice = MagicMock()
            mock_choice.message.content = None
            MockOpenAI.return_value.chat.completions.create.return_value = MagicMock(
                choices=[mock_choice]
            )
            client = OllamaLLMClient(model="llama3.2")
            assert client.generate("sys", "user") == ""

    def test_openai_compatible_endpoint_used(self) -> None:
        with patch("src.generation.ollama_client.OpenAI") as MockOpenAI:
            OllamaLLMClient(model="llama3.2", base_url="http://localhost:11434")
            call_kwargs = MockOpenAI.call_args[1]
            assert "http://localhost:11434/v1" in call_kwargs.get("base_url", "")

    def test_default_temperature_is_point_one(self) -> None:
        with patch("src.generation.ollama_client.OpenAI"):
            client = OllamaLLMClient(model="llama3.2")
        assert client.temperature == 0.1

    def test_default_max_tokens_is_1024(self) -> None:
        with patch("src.generation.ollama_client.OpenAI"):
            client = OllamaLLMClient(model="llama3.2")
        assert client.max_tokens == 1024

    def test_custom_temperature_and_max_tokens_stored(self) -> None:
        with patch("src.generation.ollama_client.OpenAI"):
            client = OllamaLLMClient(model="llama3.2", temperature=0.7, max_tokens=512)
        assert client.temperature == 0.7
        assert client.max_tokens == 512


# ---------------------------------------------------------------------------
# OllamaLLMClient.generate_stream
# ---------------------------------------------------------------------------

class TestOllamaLLMClientGenerateStream:
    def _stream_chunks(self, tokens: list[str | None]):
        """Build a mock streaming iterator from a list of token strings (None = empty delta)."""
        for token in tokens:
            chunk = MagicMock()
            chunk.choices[0].delta.content = token
            yield chunk

    def test_yields_tokens_as_strings(self) -> None:
        with patch("src.generation.ollama_client.OpenAI") as MockOpenAI:
            MockOpenAI.return_value.chat.completions.create.side_effect = (
                lambda **kw: self._stream_chunks(["Hello", " world", "."])
            )
            client = OllamaLLMClient(model="llama3.2")
            tokens = list(client.generate_stream(
                system_prompt="You are helpful.",
                messages=[{"role": "user", "content": "Say hello."}],
            ))
        assert tokens == ["Hello", " world", "."]

    def test_skips_none_delta_content(self) -> None:
        with patch("src.generation.ollama_client.OpenAI") as MockOpenAI:
            MockOpenAI.return_value.chat.completions.create.side_effect = (
                lambda **kw: self._stream_chunks(["Hello", None, "."])
            )
            client = OllamaLLMClient(model="llama3.2")
            tokens = list(client.generate_stream("sys", [{"role": "user", "content": "hi"}]))
        assert None not in tokens
        assert "Hello" in tokens
        assert "." in tokens

    def test_empty_stream_yields_nothing(self) -> None:
        with patch("src.generation.ollama_client.OpenAI") as MockOpenAI:
            MockOpenAI.return_value.chat.completions.create.side_effect = (
                lambda **kw: iter([])
            )
            client = OllamaLLMClient(model="llama3.2")
            tokens = list(client.generate_stream("sys", [{"role": "user", "content": "hi"}]))
        assert tokens == []

    def test_system_prompt_prepended_to_messages(self) -> None:
        captured: list[dict] = []

        def _capture(**kwargs: object) -> object:
            captured.extend(kwargs.get("messages", []))  # type: ignore[arg-type]
            return iter([])

        with patch("src.generation.ollama_client.OpenAI") as MockOpenAI:
            MockOpenAI.return_value.chat.completions.create.side_effect = _capture
            client = OllamaLLMClient(model="llama3.2")
            list(client.generate_stream(
                system_prompt="Be concise.",
                messages=[{"role": "user", "content": "Hello."}],
            ))

        assert captured[0]["role"] == "system"
        assert captured[0]["content"] == "Be concise."

    def test_stream_flag_passed_to_create(self) -> None:
        calls: list[dict] = []

        def _record(**kwargs: object) -> object:
            calls.append(dict(kwargs))
            return iter([])

        with patch("src.generation.ollama_client.OpenAI") as MockOpenAI:
            MockOpenAI.return_value.chat.completions.create.side_effect = _record
            client = OllamaLLMClient(model="llama3.2")
            list(client.generate_stream("sys", [{"role": "user", "content": "hi"}]))

        assert calls[0].get("stream") is True
