# raw_sources/

This directory holds **immutable primary legal sources**. The wiki under
`knowledge_base/` paraphrases and cites them; nothing in this directory
is ever modified by an agent or by automated tooling.

## Layer permissions

Per `AGENTS.md`:

- Agents (Claude Code, Copilot, others) have **read-only** access.
- The human maintainer is the only writer.
- Files are tracked via Git LFS (see `.gitattributes`).

## Subdirectories

| Path                     | Contents                                         |
|--------------------------|--------------------------------------------------|
| `raw_sources/acts/`      | Consolidated Acts (TPA, DRCA, RERA, Reg. Act…)  |
| `raw_sources/rules/`     | Rules and notifications (Delhi RERA Rules, …)   |
| `raw_sources/forms/`     | Official court forms, vakalatnamas, e-Filing    |
| `raw_sources/stats/`     | NJDG dumps, Daksh datasets, public court stats  |
| `raw_sources/circulars/` | Government circulars, MCD/DDA notifications     |

## Permitted source provenance

A file may be added to `raw_sources/` only if it comes from one of:

1. **India Code** — `https://www.indiacode.nic.in/`
2. **Delhi Government Legislative Department** — official Delhi GoI publications
3. **e-Gazette of India** — `https://egazette.gov.in/`
4. **Delhi High Court** — `https://delhihighcourt.nic.in/`
5. **National Judicial Data Grid** — `https://njdg.ecourts.gov.in/`
6. **Ministry of Law and Justice** publications
7. **Statutory authority publications** — DSLSA, DHCLSC, Delhi RERA, DDA, MCD

Files from law firms, private publishers, secondary commentaries, blog
posts, or social media are NOT permitted here. Such material may inform
the human's understanding but cannot serve as a primary source for any
wiki claim.

## File naming convention

`<jurisdiction>_<short-name>_<year>[_section_or_part].<ext>`

Examples:
- `central_tpa_1882.pdf`
- `central_registration_act_1908.pdf`
- `delhi_drca_1958.pdf`
- `delhi_rera_rules_2017.pdf`
- `delhi_hc_rules_civil_2018.pdf`
- `njdg_disposal_delhi_2025_q4.csv`

Use lowercase, underscore-separated, ASCII-only. The filename is part
of the citation chain: agents reference these paths verbatim in PRs
and lint reports.

## Provenance log

For each file added here, include a one-line entry in
`raw_sources/PROVENANCE.md` (create if absent):

```
- central_tpa_1882.pdf — Downloaded 2026-05-20 from
  https://www.indiacode.nic.in/handle/123456789/2338, SHA256 <hash>.
```

The SHA256 lets future readers verify that the file has not silently
changed.

## What this directory is NOT

- It is not a search corpus. The retrieval pipeline in `src/` indexes
  `knowledge_base/`, not `raw_sources/`.
- It is not where the LLM writes summaries. Summaries live in
  `knowledge_base/`.
- It is not a redistribution channel. The files here are public
  documents under Government of India copyright; their inclusion in
  this repository is a fair-use research mirror, not a license to
  redistribute commercially.

## When a source is amended

When an Act, rule, or notification is amended:

1. **Do NOT overwrite** the existing file. Keep historical text
   recoverable from Git LFS history is fragile across rebases.
2. Add the new version as a separate file with the amendment year:
   `central_tpa_1882_amended_2002.pdf`.
3. Note both files in `PROVENANCE.md`.
4. Trigger an ingest (see
   `.claude/skills/primary-source-ingest/SKILL.md`) to update affected
   wiki articles.
5. Affected articles' `last_reviewed` resets to `null` automatically
   per the ingest skill.
