"""Smoke test that the refusal message is well-formed."""
from src.generation.prompts import REFUSAL_MESSAGE


def test_refusal_mentions_dslsa():
    assert "1516" in REFUSAL_MESSAGE
    assert "Nyaaya" in REFUSAL_MESSAGE
