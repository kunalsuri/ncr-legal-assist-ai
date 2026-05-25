---
name: legal-citation-verifier
description: Use this skill before authoring, modifying, or reviewing any wiki page in knowledge_base/, and before generating any test fixture that contains statutory text. The skill enforces the primary-source-only rule that makes this legal-information project defensible. Trigger this skill whenever you are about to write a sentence containing a statute reference, a section number, a court fee, a procedural timeline, or any other legal fact. Do NOT skip this skill on the grounds that "the citation is obvious" or "I remember this section" — the project's value depends on every citation being verified against raw_sources/ in the current session, not against your training data.
---

# Legal Citation Verifier

## When to use this skill

Read this `SKILL.md` before:

1. Authoring or modifying any file under `knowledge_base/statutes/`,
   `knowledge_base/concepts/`, or `knowledge_base/entities/`.
2. Generating test fixtures that contain statutory text or citations.
3. Reviewing a pull request that touches any of the above.
4. Answering a human's question with a claim that includes a section
   number, court fee, timeline, or procedural step.

If you find yourself about to type "[TPA §106]" or "Section 27 of the
Delhi Rent Control Act provides…" without having opened the
corresponding file in `raw_sources/` in the current session, stop and
read this skill first.

## The verification protocol

For each factual claim you are about to make, run the following checks
in order. If any check fails, do not write the claim.

### Check 1 — Primary source is present

The Act, rule, form, or statistic must exist as a file under
`raw_sources/`. Run:

```bash
ls raw_sources/acts/ raw_sources/rules/ raw_sources/forms/ raw_sources/stats/
```

If the source file is not present, the claim cannot be made. Tell the
human which raw source needs to be added before this content can be
written.

### Check 2 — You have read the relevant section in this session

Open the source file with `view` and locate the specific section,
clause, or paragraph you are about to cite. Do not rely on memory or
on the file's existence alone. Read the exact text of the provision in
the current session.

For PDF sources, use the `pdf-reading` skill if it is available; for
HTML or Markdown sources, use `view` directly.

### Check 3 — The citation format matches the schema

The citation in the article body must use the form:

```
[<act-short-name> §<section>(<subsection>)]
```

Examples that are well-formed:
- `[TPA §106]`
- `[TPA §108(q)]`
- `[DRCA §27]`
- `[RERA §31]`
- `[Reg. Act §17(1)(d)]`

Examples that are NOT well-formed (reject these):
- `[Transfer of Property Act]` — missing section
- `[Section 106]` — missing Act
- `[TPA Section 106]` — wrong delimiter
- `[TPA §106, as held in Smith v. Jones]` — case law in a statute citation

### Check 4 — The frontmatter `primary_sources` list contains this Act

Open the article's frontmatter. Confirm that the Act you are citing
appears in `primary_sources` with the section in its `sections` list.
If it does not, add it before writing the body claim. The frontmatter
list and the in-body citations must agree exactly.

### Check 5 — The paraphrase is not a quotation

Compare your draft sentence against the source text. If more than
seven consecutive words match the source verbatim, rewrite. Statutory
text is Crown copyright in some jurisdictions and Government of India
copyright in others; paraphrase is also the discipline that prevents
context-free quotation.

### Check 6 — No interpretive language

Reject sentences containing any of:

- "the courts have held"
- "in practice"
- "this generally means"
- "lawyers typically"
- "the better view is"
- "it is well settled"
- "implicitly"
- "by analogy"

These phrases mark interpretation, not statement of statutory text.
Interpretation belongs to advocates and judges, not to this project.

## The article-level checklist

Before opening a PR for any new or modified wiki article, confirm:

- [ ] Every paragraph in the body ends with at least one citation.
- [ ] Every Act cited in the body appears in `primary_sources`.
- [ ] No Act in `primary_sources` is unused in the body (no dangling).
- [ ] `status` is `unreviewed-primary-sources-only` (unless a reviewer
      is supplied).
- [ ] `last_reviewed` is `null` and `reviewer` is `null` (same
      condition).
- [ ] `disclaimer_level` is `high`.
- [ ] The article body contains no interpretive language (Check 6).
- [ ] If the article is in `knowledge_base/concepts/` or
      `knowledge_base/entities/`, it contains only pointers and
      constitutive citations, not re-derived statutory content.

If any item fails, fix it before opening the PR.

## The PR-level checklist

In every PR description that touches `knowledge_base/`, include:

```markdown
## Citation verification

- Raw source(s) consulted: <list of files under raw_sources/>
- Wiki pages modified: <list>
- Citations added: <count>
- Citations removed: <count>
- Frontmatter `primary_sources` updated: yes / no
- Interpretive language present: no
- Paraphrase verbatim-match check: passed (< 7 consecutive words)
```

## When verification fails

If you cannot verify a claim against `raw_sources/` in the current
session, the correct action is to:

1. Not write the claim.
2. Tell the human which primary source needs to be added, and exactly
   which section.
3. Stop and wait.

Writing an unverified claim, even one you are highly confident about,
defeats the project. The friend or family member who ends up acting on
that claim has no way to know it was the one in fifty that the
verifier did not catch. Treat verification as a hard gate, not a
guideline.

## What this skill does NOT cover

This skill verifies that wiki content is grounded in primary sources.
It does NOT verify:

- That the primary source is currently in force (amendments, repeals).
  That is the reviewer's job; until a reviewer signs off, articles
  carry `status: unreviewed-primary-sources-only` precisely to flag
  this gap to readers.
- That the paraphrase is the most useful or pedagogically clear one.
  That is editorial judgement, exercised at human review.
- That the article is complete. Articles can be incomplete; what they
  cannot be is wrong.
