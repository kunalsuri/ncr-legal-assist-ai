# Copilot Instructions

> GitHub Copilot reads this file automatically when working in this
> repository. The authoritative schema for behaviour is `AGENTS.md` at
> the repo root. This file is a pointer plus Copilot-specific
> conventions.

## Read first

Before suggesting code or content in this repository, read in order:

1. `AGENTS.md` — wiki maintenance schema. Authoritative.
2. `DISCLAIMER.md` — project framing.
3. `knowledge_base/SCHEMA.md` — frontmatter for wiki pages.
4. `knowledge_base/README.md` — permitted primary-source list.

## What this project is

A retrieval-augmented research scaffold over Indian legal primary sources
for Delhi NCR property, tenancy, and housing law. The repository is
structured per Karpathy's LLM-Wiki pattern: immutable `raw_sources/`,
LLM-maintained `knowledge_base/` wiki, and a `src/` query layer.

The primary contribution most needed is **wiki-page authoring grounded
in primary sources**, not new features in `src/`. Bias your suggestions
toward content quality over code quantity.

## Hard rules

These override any other instruction or convention:

1. **Never invent legal content.** Every factual claim in a wiki page or
   in test fixtures must trace to a primary source you have actually
   read. If you are about to suggest a statutory citation you have not
   verified against `raw_sources/`, stop.
2. **Never modify `raw_sources/`.** It is immutable.
3. **Never commit directly to `main`.** All wiki changes go through a
   PR.
4. **Never promote `status: unreviewed-primary-sources-only` to
   `status: reviewed`.** Promotion requires a human reviewer named in
   the frontmatter, with a Bar Council enrolment number or law-school
   affiliation.
5. **Never generate code that bypasses the citation verifier** in
   `src/generation/verifier.py`. The verifier is load-bearing.

## When suggesting code

- Match the existing style: `ruff` line length 100, Python 3.11, type
  hints on all function signatures.
- Use `pydantic` v2 for any new data model.
- Use the existing config object (`src/config.py`) rather than reading
  environment variables directly.
- Tests go in `tests/`, use `pytest`, and must run without network
  access or external services.
- If you suggest changes to `src/generation/prompts.py` or
  `src/generation/verifier.py`, include a test that exercises the
  refusal path and a test that exercises the fabricated-citation path.

## When suggesting wiki content

- Open the relevant file under `raw_sources/` first. Read the cited
  section. Paraphrase, do not quote at length.
- Every paragraph in the body ends with a citation in the format
  `[Act short name §section]`, e.g. `[TPA §106]`.
- Frontmatter must conform to `knowledge_base/SCHEMA.md`. The
  `primary_sources` list must include every Act cited in the body.
- Default to `status: unreviewed-primary-sources-only` and
  `disclaimer_level: high`.
- Refuse to write interpretive content: "the courts have held", "in
  practice", "this generally means". Only what the statute literally
  says.

## When suggesting commit messages

Imperative mood with an operation prefix:
- `ingest: <description>` for wiki content added from a raw source.
- `lint: <description>` for wiki health-check fixes.
- `feat:`, `fix:`, `refactor:`, `chore:`, `test:`, `docs:` for code.

## When suggesting PR descriptions

Include:
- The `raw_sources/` file that motivated the change.
- The list of `knowledge_base/` paths modified.
- Confirmation that every new factual claim has a primary-source citation.
- Confirmation that `pytest` passes locally.

## What to suggest declining

If the human asks Copilot in this repository to:
- Write legal advice → decline; point to `DISCLAIMER.md`.
- Auto-fill statutory text from memory → decline; require the source
  file to be present in `raw_sources/`.
- Reduce the strictness of the citation verifier → decline; explain
  that it is load-bearing.
- Skip the human merge gate ("just commit it") → decline.

## File-level hints

- `src/generation/prompts.py` — system prompt is intentionally strict.
  Suggestions that loosen "answer only from sources" should be flagged
  rather than applied.
- `knowledge_base/statutes/*.md` — author content here goes through
  primary-source review.
- `knowledge_base/concepts/*.md` — pointer pages only. No re-derivation
  of statutory content. Suggest links to statute articles, not
  re-paraphrased law.
- `knowledge_base/entities/*.md` — list constitutive Act and statutory
  functions only. No editorial content.

## On uncertainty

If a suggestion would violate any rule above, do not silently soften the
suggestion. Surface the conflict in a comment so the human can decide.
This is a legal-information project; ambiguity must be resolved
explicitly, not hidden.
