---
name: primary-source-ingest
description: Use this skill whenever the human asks you to ingest, process, integrate, or "read in" a new source from raw_sources/ into the knowledge base. Triggers include any message containing "ingest", "process this PDF", "add this Act to the wiki", "integrate the new gazette notification", or simply pointing at a file under raw_sources/ and asking what should change in knowledge_base/. This skill defines the full PR-gated ingest workflow that maintains the wiki's integrity. Do NOT begin reading the source or proposing changes without reading this skill first; the order of operations matters because the human's confirmation step (Phase 2) is what prevents silent over-scoping.
---

# Primary Source Ingest

## When to use this skill

Read this `SKILL.md` whenever a new file appears under `raw_sources/`
and the human asks you to integrate it into the wiki. Typical
triggers:

- "Ingest `raw_sources/acts/tpa_1882.pdf`."
- "I added the Delhi RERA Rules. Process them."
- "Read this gazette notification and update the wiki."
- "What changes are needed in `knowledge_base/` after this Act?"

Do not run an informal version of this workflow. The phases below
exist because legal-content ingest fails in specific ways that the
schema is designed to prevent.

## Prerequisites

Before starting Phase 1, confirm:

- `AGENTS.md` has been read in this session.
- `legal-citation-verifier` SKILL.md has been read in this session.
- `knowledge_base/SCHEMA.md` has been read in this session.
- The source file is actually present at the path the human cited.
- The source is on the permitted list in `knowledge_base/README.md`.
  If it is not (e.g. a law-firm blog, a private practitioner's
  commentary), refuse the ingest and explain why.

If any prerequisite fails, do not proceed.

## Phase 1 — Read

Open the source file. For a PDF, use the `pdf-reading` skill. For
HTML, use `view`.

Read the source in full, not just the sections the human named. You
need to know what is in the document so that you can identify which
existing wiki pages it affects beyond the obvious target.

Produce, internally:

- A table of contents or section list of the source.
- The 3–8 sections most relevant to the project's scope (Delhi NCR
  property, tenancy, housing).
- A list of existing wiki pages that this source affects (from
  `knowledge_base/index.md`).
- A list of new wiki pages this source warrants (statute articles,
  concept pages, entity pages).

Do not write any file yet.

## Phase 2 — Discuss with the human

Present the lists above to the human in chat. Use this exact
structure:

```
## Ingest plan for <source-id>

**Source**: <raw_sources/path>
**Sections in scope**: <list with one-line summaries>

**Existing wiki pages affected**:
- <article_id> — <one-line description of change>
- ...

**New wiki pages proposed**:
- <article_id> — <one-line description, with target directory>
- ...

**Out of scope (read but not ingested)**:
- <sections of the source not relevant to this project>

Proceed?
```

Wait for explicit confirmation. The human may narrow the scope ("only
do Section 106 for now"), expand it ("also add the cross-reference
from the Registration Act"), or reject ("this is RERA-Haryana, we are
Delhi-only").

Do not begin Phase 3 without confirmation. Implicit confirmation does
not count.

## Phase 3 — Branch

Create the branch:

```bash
git checkout -b ingest/<source-id>
```

Where `<source-id>` matches the slug used in the wiki (e.g.
`ingest/tpa-1882-s106` or `ingest/delhi-rera-rules-2017`).

## Phase 4 — Write

For each new or modified wiki page:

1. Open the source file at the exact section to be cited.
2. Paraphrase the section in plain English.
3. Apply every check in `legal-citation-verifier/SKILL.md`.
4. Update or create the frontmatter per
   `knowledge_base/SCHEMA.md`.
5. For concept pages: add only pointers (links to statute articles).
   Do not re-derive content.
6. For entity pages: state the constitutive Act and statutory
   functions only.

Update `knowledge_base/index.md`: add a one-line catalog entry per
new page, update entries for modified pages, keep the file sorted by
category and article ID.

Append to `knowledge_base/log.md` a single entry:

```markdown
## [YYYY-MM-DD] ingest | <source-id>

- Source: `<raw_sources/path>`
- New pages: <list of article_ids>
- Updated pages: <list of article_ids>
- Cross-references added: <count>
- Branch: `ingest/<source-id>`
```

Use the actual date in ISO format. The consistent prefix `## [`
matters for log parsing.

## Phase 5 — Self-check

Before opening the PR, run:

```bash
pytest -v
ruff check src tests scripts
```

Both must pass.

Re-read each new or modified wiki page once. Apply the article-level
checklist from `legal-citation-verifier/SKILL.md`.

If any check fails, fix it. Do not open the PR with known issues
and a note saying "the human can review."

## Phase 6 — Open the PR

```bash
git add knowledge_base/
git commit -m "ingest: <one-line description>"
git push origin ingest/<source-id>
```

Open the PR. Include in the description:

```markdown
## Ingest summary

**Source**: `<raw_sources/path>`

## Wiki changes

**New pages**:
- <article_id> (<target directory>)

**Updated pages**:
- <article_id> — <what changed>

**Cross-references added** (in concept/entity pages):
- <count>

## Citation verification

- Raw sources consulted in this session: <list>
- Citations added: <count>
- Frontmatter `primary_sources` updated: yes
- Interpretive language present: no
- Paraphrase verbatim-match check: passed

## Next steps

- Human review of paraphrase accuracy against `<raw_sources/path>`.
- `pytest` must pass on CI before merge.
- After merge, run `make build-index` to rebuild the retrieval index.
```

## Phase 7 — Wait

Do not merge. Do not amend the PR after opening unless the human
asks. The human reviews against the raw source, runs the citation
verifier, and merges manually.

If the human requests changes:

1. Apply them on the same branch.
2. Re-run Phase 5 self-checks.
3. Push the amended branch.

## Common failure modes (and what to do)

- **Source is unreadable** (scanned PDF without OCR): tell the
  human; do not attempt to OCR silently. Suggest running OCR as a
  separate step and re-running the ingest.
- **Source contradicts an existing article**: do not silently
  overwrite. Open the PR with both versions side by side in the PR
  description, and ask the human to choose.
- **Source is partially in scope**: ingest only the in-scope
  sections; list the out-of-scope sections in the PR description so
  they are visible for future ingests.
- **Source is an amendment**: the affected article's
  `last_reviewed` must be reset to `null` and `reviewer` must be
  reset to `null`, because a reviewed pre-amendment article is no
  longer reviewed post-amendment. Mention this explicitly in the PR.
- **You are uncertain whether a section is in scope**: ask the human
  in Phase 2. Do not guess.

## What ingest does NOT do

- Ingest does NOT promote any article to `status: reviewed`.
- Ingest does NOT modify files under `raw_sources/`.
- Ingest does NOT touch `src/`. If the source reveals a code issue
  (e.g. the embedding model handles a particular term poorly), open a
  separate PR for that.
- Ingest does NOT re-run the retrieval index. That is the human's
  step after merge.
