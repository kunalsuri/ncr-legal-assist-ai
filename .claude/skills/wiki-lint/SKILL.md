---
name: wiki-lint
description: Use this skill when the human asks for a wiki health check, audit, hygiene pass, or lint of the knowledge base. Triggers include "lint the wiki", "what's stale in knowledge_base", "audit the citations", "find orphan pages", or any periodic maintenance request. The skill defines a deterministic, repeatable audit pass that produces a Markdown lint report under knowledge_base/lint_reports/. Do NOT fix issues silently as you find them; the protocol is to report first, then fix in a separate PR per issue cluster, so the human can see the wiki's drift over time.
---

# Wiki Lint

## When to use this skill

Read this `SKILL.md` whenever the human asks for a maintenance pass
on the knowledge base. Typical triggers:

- "Lint the wiki."
- "Health-check `knowledge_base/`."
- "What's stale?"
- "Find orphan pages."
- "Audit citations."
- Periodic prompts ("monthly hygiene", "before tagging v0.3").

The output of this skill is a lint report. The output is NOT silent
fixes. Drift over time is information; hiding it from the human
removes the signal that this project is healthy or unhealthy.

## The protocol

### Phase 1 — Read what is there

Open and read:

- `knowledge_base/index.md`
- `knowledge_base/log.md`
- All files under `knowledge_base/statutes/`,
  `knowledge_base/concepts/`, `knowledge_base/entities/`.
- The last lint report in `knowledge_base/lint_reports/`, if any.

You are looking for state, not making changes yet.

### Phase 2 — Run the eight checks

For each check below, build a list of offending files or claims.

#### Check A — Empty or invalid frontmatter

Every wiki page must have frontmatter conforming to
`knowledge_base/SCHEMA.md`. Flag pages where:

- The frontmatter is missing entirely.
- A required field is absent.
- An enum field has an invalid value (e.g. `status: draft` is not in
  the schema).

#### Check B — Empty `primary_sources` list

Any article with a non-empty body whose frontmatter
`primary_sources` list is empty. This is a tier-1 violation: it
means the article makes claims that are not traceable to a primary
source.

#### Check C — Broken primary-source URLs

For each entry in any article's `primary_sources`, the `url` field
must resolve. Flag entries where the URL returns 404, redirects to
an unrelated page, or has an obviously malformed format. You do not
need to perform live HTTP checks if the network is unavailable;
flag suspicious URLs (typos, missing schemes) for human verification.

#### Check D — Silent citations

Scan article bodies for citation strings of the form `[<Act> §<n>]`.
For each citation found in the body, the Act must appear in the
article's frontmatter `primary_sources` with that section in
`sections`. Flag mismatches.

This is the most common failure mode: an author writes "the Act also
allows X [TPA §107]" without updating frontmatter.

#### Check E — Stale articles

Flag articles where:

- `last_reviewed` is more than 18 months in the past.
- `status: reviewed` but the source PDF in `raw_sources/` has been
  modified (check `git log` on the source file) after `last_reviewed`.

The second condition catches amendments that may have superseded a
reviewed article.

#### Check F — Orphan concept and entity pages

For each file in `knowledge_base/concepts/` and
`knowledge_base/entities/`, count inbound links from
`knowledge_base/statutes/` and from other concept/entity pages.

Flag any page with zero inbound links. Concept and entity pages
exist to be linked TO; an orphan is dead weight.

#### Check G — Missing concept pages

Scan statute articles for statutory terms of art that recur across
three or more articles without a corresponding concept page.
Candidates include: "notice", "registration", "limitation",
"specific performance", "easement", "mutation", "vakalatnama".

Flag terms that appear in many articles but have no concept page.
Do NOT auto-create the page; the human decides whether the concept
warrants its own page.

#### Check H — Interpretive language in bodies

Grep article bodies for forbidden phrases (per
`legal-citation-verifier/SKILL.md` Check 6):

- "the courts have held"
- "in practice"
- "this generally means"
- "lawyers typically"
- "the better view is"
- "it is well settled"
- "implicitly"
- "by analogy"

Flag every occurrence with file and line number.

### Phase 3 — Write the lint report

Create `knowledge_base/lint_reports/lint-YYYY-MM-DD.md` with this
exact structure:

```markdown
---
date: YYYY-MM-DD
lint_pass: <integer, increment from previous report>
total_articles_scanned: <count>
total_issues: <count>
---

# Wiki Lint Report — YYYY-MM-DD

## Summary

- Articles scanned: <count>
- Issues by severity:
  - Critical (Checks B, D): <count>
  - High (Checks A, C, H): <count>
  - Medium (Checks E, F): <count>
  - Low (Check G): <count>

## Critical — Untraceable claims

### Check B — Empty `primary_sources`

<file:line list, or "none">

### Check D — Silent citations (body cites Act not in frontmatter)

<file:line list with the offending citation, or "none">

## High — Structural integrity

### Check A — Invalid frontmatter

<file list with the specific field that fails, or "none">

### Check C — Broken or suspicious primary-source URLs

<file list with the suspect URL, or "none">

### Check H — Interpretive language

<file:line list with the offending phrase, or "none">

## Medium — Currency and connectivity

### Check E — Stale or post-amendment articles

<file list with last_reviewed date and reason, or "none">

### Check F — Orphan concept and entity pages

<file list, or "none">

## Low — Coverage gaps

### Check G — Recurring terms without a concept page

<term list with article count, or "none">

## Recommended PRs

A grouping of issues into PR-sized clusters. One PR per cluster.

1. <PR title> — fixes: <issue ids from above>
2. ...

## Append to log.md

```markdown
## [YYYY-MM-DD] lint | pass <integer>

- Articles scanned: <count>
- Critical issues: <count>
- High issues: <count>
- Medium issues: <count>
- Low issues: <count>
- Report: `knowledge_base/lint_reports/lint-YYYY-MM-DD.md`
```
```

### Phase 4 — Open one PR per recommended cluster

After the human reads the lint report and confirms the cluster plan:

For each cluster:

1. Create a branch `lint/YYYY-MM-DD-cluster-<n>`.
2. Apply the fixes within that cluster only.
3. Re-run the relevant `legal-citation-verifier` checks on every
   modified file.
4. Open a PR titled `lint: <cluster description>`.
5. Reference the lint report in the PR description.

Do not bundle unrelated fixes. The whole point of cluster PRs is
that the human can review each focused change against the source.

### Phase 5 — Wait for merges

Do not merge any lint PR yourself.

## Severity escalation

If Check B or Check D finds more than five offenders, escalate to
the human immediately, before completing the lint report. A spike in
critical issues signals systemic drift (e.g. a recent ingest skipped
the verifier skill), and the human should investigate before more
content lands on the bad foundation.

## What lint does NOT do

- Lint does NOT promote articles from `unreviewed-primary-sources-only`
  to `reviewed`. That is reviewer work, not lint work.
- Lint does NOT modify `raw_sources/`.
- Lint does NOT delete articles, even orphans. Orphans are flagged
  for the human to decide.
- Lint does NOT rewrite paraphrases for clarity or style. Lint
  enforces the schema; editorial improvements are separate PRs.
- Lint does NOT re-run the retrieval index. That happens after the
  human merges lint PRs.

## Cadence

Run lint at minimum once a month. Run lint before tagging any
release (`v0.2`, `v0.3`, etc.). Run lint immediately after a batch
of ingests that touched five or more articles. Run lint whenever a
reviewer asks "is the wiki ready for review."
