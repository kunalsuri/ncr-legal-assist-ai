# AGENTS.md — Wiki Maintenance Schema

> **Authoritative.** This file defines the behavioural schema for every
> AI agent operating in `ncr-legal-assist-ai`. All other agent-facing
> files (`CLAUDE.md`, `.github/copilot-instructions.md`,
> `.claude/skills/*/SKILL.md`) defer to this file. When they conflict,
> this file wins.

---

## 1. What this project is

`ncr-legal-assist-ai` is a retrieval-augmented research scaffold over
Indian legal primary sources for Delhi NCR property, tenancy, and housing
law. It follows the **Karpathy LLM-Wiki pattern** adapted for a legal
domain:

- `raw_sources/` — immutable primary documents (PDFs, CSV, XLSX)
- `knowledge_base/` — a wiki of paraphrased articles with strict citation
- `src/` — a RAG query layer over the wiki

This is software, not a legal service. See `DISCLAIMER.md`.

---

## 2. Layer permissions

| Layer            | Path                   | Agents may…            | Only humans may…       |
|------------------|------------------------|------------------------|------------------------|
| Primary sources  | `raw_sources/`         | Read only              | Add, rename, delete    |
| Knowledge base   | `knowledge_base/`      | Read; propose via PR   | Merge to `main`        |
| Query layer      | `src/`, `tests/`       | Read; propose via PR   | Merge to `main`        |
| Config/tooling   | `pyproject.toml`, etc. | Read; propose via PR   | Merge to `main`        |
| Schema / schema  | `AGENTS.md`, `SCHEMA.md` | Read only            | Modify                 |

**No agent commits directly to `main`. Ever.**

---

## 3. The primary-source rule

Every factual sentence in any `knowledge_base/` article must be traceable
to a specific section or provision of a specific primary source held in
`raw_sources/` **that the agent has actually read in the current session**.

### What counts as a primary source

- Central Acts available on **India Code** (`indiacode.nic.in`)
- Delhi-specific Acts from **Delhi Government Legislative Department**
- Rules and notifications from **e-Gazette** (`egazette.gov.in`)
- Court rules and forms from **Delhi High Court** (`delhihighcourt.nic.in`)
- Procedural data from **NJDG** (`njdg.ecourts.gov.in`)
- Publications from **Ministry of Law and Justice**
- Statutory authority publications (DSLSA, DHCLSC, Delhi RERA, DDA, MCD)

### What does NOT count

- Secondary commentary (Nyaaya, law firm blogs, academic articles)
- Training data or prior knowledge of the statute
- Summaries from any source not listed above

If the relevant `raw_sources/` file is absent, **stop and tell the human**
before proceeding. Do not paraphrase from memory.

---

## 4. Ingest workflow

Use `.claude/skills/primary-source-ingest/SKILL.md` for the full protocol.
Summary:

1. A human adds a file to `raw_sources/` and pushes to a branch named
   `ingest/<source-id>`.
2. The agent reads the source file in full.
3. The agent runs the citation verifier (`.claude/skills/legal-citation-verifier/SKILL.md`)
   on every claim before writing.
4. The agent proposes a PR with a new or updated `knowledge_base/` article.
5. The PR description includes the source path, modified KB paths, and the
   citation-verification checklist.
6. **The human merges. The agent does not.**

---

## 5. Query workflow

When the system answers a user query at runtime:

1. The hybrid retriever fetches chunks from the KB (BM25 + dense + reranker).
2. If confidence (rerank score) is below threshold, the system **refuses**
   rather than answering.
3. The LLM generates a response under a strict cite-or-refuse system prompt.
4. The citation verifier confirms every citation in the response maps to a
   retrieved source chunk.
5. The response is shown with the sources panel.

Agents modifying `src/` must not weaken the confidence gate or the
citation verifier. Both are load-bearing.

---

## 6. Lint workflow

Use `.claude/skills/wiki-lint/SKILL.md` for the full protocol. A lint
pass checks:

1. Every `knowledge_base/` file has valid YAML frontmatter per `knowledge_base/SCHEMA.md`.
2. No article has `status: reviewed` without a named reviewer and credential.
3. Every citation in article bodies is in the format `[Act short name §section]`.
4. No orphan concept pages (every concept page links to at least one statute article).
5. Every statute referenced in `primary_sources` frontmatter has a corresponding
   file in `raw_sources/` (or is flagged as `raw_source_pending: true`).

Lint runs on branch `lint/<yyyy-mm-dd>` and opens a PR summarising findings.

---

## 7. Forbidden actions

An agent operating in this repository must never:

- Write legal advice for a specific situation.
- Write a factual claim without a primary-source citation verified in the
  current session.
- Modify any file under `raw_sources/`.
- Commit directly to `main`.
- Promote an article from `status: unreviewed-primary-sources-only` to
  `status: reviewed` without a reviewer name and Bar Council enrolment
  number or law-school affiliation supplied by the human.
- Generate code that bypasses or weakens `src/generation/verifier.py`.
- Merge a pull request.
- Fabricate a `raw_sources/` file path that does not actually exist.

---

## 8. Branching and commit conventions

### Branches

| Operation     | Branch name pattern          |
|---------------|------------------------------|
| Ingest        | `ingest/<source-id>`         |
| Lint          | `lint/<yyyy-mm-dd>`          |
| Code feature  | `feat/<short-description>`   |
| Code fix      | `fix/<short-description>`    |

### Commit prefixes

| Prefix      | When to use                                              |
|-------------|----------------------------------------------------------|
| `ingest:`   | Wiki content added or updated from a raw source          |
| `lint:`     | Wiki health-check fixes                                  |
| `feat:`     | New feature in `src/` or tooling                         |
| `fix:`      | Bug fix in `src/` or tests                               |
| `refactor:` | Code reorganisation with no behaviour change             |
| `test:`     | New or updated tests                                     |
| `docs:`     | Documentation only                                       |
| `chore:`    | Build, config, dependency updates                        |

### PR descriptions must include

1. The `raw_sources/` file that motivated the change (for ingest PRs).
2. The list of `knowledge_base/` paths modified.
3. A confirmation that every new factual claim has a verified primary-source
   citation.
4. A confirmation that `pytest` passes locally.

---

## 9. Status promotion rule

A `knowledge_base/` article may only transition to `status: reviewed` when
a human supplies, in the PR or issue, **all** of the following:

- Reviewer full name
- Bar Council enrolment number **or** law school and faculty position
- Confirmation of which sections were read
- ISO date of review

The agent records these in the article frontmatter. The agent does not
assess the reviewer's credentials; that is the human maintainer's
responsibility.

---

## 10. Citation format

All in-body citations must use the format:

```
[Act short name §section]
```

Examples:
- `[TPA §106]`
- `[DRCA §27]`
- `[Delhi RERA Rules r.3(1)]`
- `[Registration Act §17]`

The `primary_sources` frontmatter list must include every Act cited in the
body. The act names in `primary_sources` must use the full official name
and year (e.g. `"Transfer of Property Act, 1882"`).

---

## 11. Skills

Three skills are available under `.claude/skills/`. They are **mandatory**
reads before the corresponding operation — not optional enhancement.

| Skill                      | Path                                           | Trigger condition                               |
|----------------------------|------------------------------------------------|-------------------------------------------------|
| `legal-citation-verifier`  | `.claude/skills/legal-citation-verifier/SKILL.md`  | Before writing any wiki content or statutory fixture |
| `primary-source-ingest`    | `.claude/skills/primary-source-ingest/SKILL.md`    | When ingesting a new `raw_sources/` document    |
| `wiki-lint`                | `.claude/skills/wiki-lint/SKILL.md`                | When running a health check of the wiki         |

---

## 12. First-session verification

To confirm the agent configuration is effective, open a new session and
run:

> Read AGENTS.md and CLAUDE.md, then list the skills available and what
> each one is for. Do not ingest anything yet.

A correctly configured session will return:
- The three-layer architecture summary
- The four required-reading files from `CLAUDE.md`
- The three skills with their trigger conditions

If the agent skips any of these, the configuration is not yet effective.
Fix it before any ingest is attempted.
