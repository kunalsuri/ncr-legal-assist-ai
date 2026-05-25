"""Post-hoc citation verification. Any answer with a fabricated citation is suppressed."""
from __future__ import annotations

import re

CITATION_PATTERN = re.compile(r"\[([a-z0-9\-]+)(?:,\s*[^\]]+)?\]")


def verify_answer(answer: str, retrieved_article_ids: set[str]) -> tuple[bool, list[str]]:
    """Return (is_valid, list_of_fabricated_ids).

    Valid means: at least one citation is present AND every cited article_id
    appears in the retrieved set.
    """
    cited = set(CITATION_PATTERN.findall(answer))
    if not cited:
        return False, []
    fabricated = sorted(cited - retrieved_article_ids)
    return (not fabricated), fabricated
