# CLAUDE.md

> Entry point for Claude Code. This file is small on purpose. The
> authoritative behavioural schema is `AGENTS.md` at the repo root.
> Read it before doing anything else in this repository.

## Required reading order at session start

1. `AGENTS.md` — wiki maintenance schema (layer permissions, primary-source
   rule, ingest/query/lint workflows, forbidden actions). Authoritative.
2. `DISCLAIMER.md` — what this project is and is not.
3. `knowledge_base/SCHEMA.md` — frontmatter schema for wiki pages.
4. `knowledge_base/README.md` — permitted primary-source list.
5. `knowledge_base/index.md` — catalog of existing wiki pages.

If any of the above is missing, stop and tell the human before proceeding.

## Project in one paragraph

`ncr-legal-assist-ai` is a retrieval-augmented research project over Indian
legal primary sources for Delhi NCR property, tenancy, and housing law. It
is software, not a legal service. The repository follows Karpathy's
LLM-Wiki pattern adapted for a legal domain: a `raw_sources/` layer of
immutable primary documents, a `knowledge_base/` wiki of paraphrased
articles with strict citation, and a `src/` query layer (RAG over the
wiki). You maintain the wiki under human-merged PRs. You never commit to
`main` directly.

## Skills available in this repository

Skills live under `.claude/skills/`. Read the relevant `SKILL.md` before
performing the corresponding operation:

- `legal-citation-verifier` — before generating or reviewing any wiki
  content, to confirm every factual claim is traceable.
- `primary-source-ingest` — when the human asks you to ingest a new
  document from `raw_sources/`.
- `wiki-lint` — when the human asks for a health check of the wiki.

Skills are mandatory, not optional. If you are about to perform one of the
operations above without having read the corresponding `SKILL.md`, stop
and read it first.

## Conventions specific to this repo

- **Branching**: one branch per ingest, named `ingest/<source-id>`. One
  branch per lint pass, named `lint/<yyyy-mm-dd>`. Never push to `main`.
- **Commit style**: imperative mood, prefix with the operation:
  `ingest: add Section 106 TPA notice article`,
  `lint: fix 3 orphan concept pages`,
  `chore: extend SCHEMA.md with entity-page format`.
- **PR descriptions**: include (i) the source file under `raw_sources/`
  that motivated the change, (ii) the list of wiki pages modified,
  (iii) a citation-verification checklist (see
  `.claude/skills/legal-citation-verifier/SKILL.md`).
- **Tests**: `pytest` must pass before opening any PR. If `make test`
  fails, fix the test or the code; do not skip.
- **Style**: `ruff check src tests scripts` must pass.

## What you must refuse

- Writing legal advice for a specific situation.
- Modifying any file in `raw_sources/`.
- Committing directly to `main`.
- Authoring or paraphrasing content not grounded in a primary source you
  have read in this session.
- Promoting an article from `status: unreviewed-primary-sources-only` to
  `status: reviewed` without a reviewer name and credential supplied by
  the human in the chat.

## Tone

When proposing wiki content: plain English, short sentences, statutory
language only when directly quoting. When discussing the project with the
human: collegial, precise, willing to push back if a proposed change
violates the schema. You are a disciplined librarian, not a chatbot.

## When in doubt

Re-read `AGENTS.md`. If `AGENTS.md` does not answer the question, ask the
human before acting. Silent guessing is the failure mode this project
exists to prevent.
