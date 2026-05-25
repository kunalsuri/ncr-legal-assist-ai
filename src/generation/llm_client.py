"""Client for a local OpenAI-compatible LLM server (vLLM, llama.cpp server)."""
from __future__ import annotations

from openai import OpenAI


class LLMClient:
    def __init__(self, endpoint: str, model: str, temperature: float, max_tokens: int) -> None:
        self.client = OpenAI(base_url=endpoint, api_key="not-needed")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or ""
