"""Tests that empty template files are skipped and valid frontmatter parses."""
from pathlib import Path
import tempfile

from src.ingestion.markdown_loader import load_kb


def test_empty_template_is_skipped():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "empty.md"
        p.write_text("---\nid: x\ntitle: x\nstatus: unreviewed-primary-sources-only\n"
                     "jurisdiction: [Delhi]\ntopic: tenancy\naudience: any\n"
                     "language: en\n---\n\n<!-- TODO -->")
        assert load_kb(Path(tmp)) == []
