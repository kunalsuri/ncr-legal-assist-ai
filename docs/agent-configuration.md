# AI Agent Configuration

This document explains how Claude Code and GitHub Copilot are configured to
behave as **disciplined wiki librarians** in this repository.

> This is adapted from [`agent-config/README.md`](../agent-config/README.md),
> which is the original bundle description.

---

## Overview: the three-layer design

The agent configuration uses three layers of files, each doing a distinct job:

### Layer 1 — `AGENTS.md` (authoritative schema)

[`AGENTS.md`](../AGENTS.md) at the repo root is tool-agnostic and is read by
both Claude Code and Copilot. It is the single authoritative source for:

- Layer permissions (who can read/write each directory)
- The primary-source rule
- Ingest, query, and lint workflows
- Forbidden actions
- Branching and commit conventions
- Status promotion rules

If `AGENTS.md` conflicts with any other file, `AGENTS.md` wins.

### Layer 2 — Tool-specific pointers

Two thin files point to `AGENTS.md` and add tool-specific conventions:

| File | Used by |
|------|---------|
| [`CLAUDE.md`](../CLAUDE.md) | Claude Code |
| [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | GitHub Copilot |

These files never duplicate behaviour defined in `AGENTS.md`; they reference
it and add IDE-specific notes (file-level hints, branching shortcuts, etc.).

### Layer 3 — Operational playbooks (skills)

Three `SKILL.md` files under `.claude/skills/` encode step-by-step protocols
for specific operations. They are **mandatory** reads before the corresponding
task — not optional guidance.

| Skill | Path | When to read |
|-------|------|--------------|
| `legal-citation-verifier` | `.claude/skills/legal-citation-verifier/SKILL.md` | Before writing any wiki content or statutory test fixture |
| `primary-source-ingest` | `.claude/skills/primary-source-ingest/SKILL.md` | When ingesting a new document from `raw_sources/` |
| `wiki-lint` | `.claude/skills/wiki-lint/SKILL.md` | When running a health check of the wiki |

---

## File placement

All agent-configuration files are in the standard locations expected by
each tool. The bundle in `agent-config/` describes the original deployment:

```
agent-config/
└── README.md    ← bundle description and setup instructions

Deployed to repo root and standard paths:

AGENTS.md                                         ← Layer 1 (authoritative)
CLAUDE.md                                         ← Layer 2 (Claude Code)
.gitattributes                                    ← Git LFS patterns
.github/
└── copilot-instructions.md                       ← Layer 2 (Copilot)
.claude/
└── skills/
    ├── legal-citation-verifier/SKILL.md          ← Layer 3
    ├── primary-source-ingest/SKILL.md            ← Layer 3
    └── wiki-lint/SKILL.md                        ← Layer 3
raw_sources/
└── README.md                                     ← Layer permissions notice
```

---

## Git LFS setup

Large binary files under `raw_sources/` (PDFs, spreadsheets, archives) are
tracked via Git LFS. The patterns are defined in `.gitattributes`.

```bash
# One-time install — Ubuntu / Debian
sudo apt-get install git-lfs

# Or on macOS
brew install git-lfs

# Or on Windows (via Chocolatey)
choco install git-lfs

# Initialise LFS in this repository
cd ncr-legal-assist-ai
git lfs install

# Confirm the patterns are picked up
git lfs track

# Add and commit
git add .gitattributes
git commit -m "chore: configure Git LFS for raw_sources/"
git push
```

After this, any PDF, image, XLSX, ZIP, or large binary placed under
`raw_sources/` is automatically pushed to LFS rather than the regular Git
pack.

---

## Verifying the configuration works

Open Claude Code (or a Copilot Chat session) in the repository and run:

> Read AGENTS.md and CLAUDE.md, then list the skills available and what
> each one is for. Do not ingest anything yet.

A correctly configured session will respond with:

1. A summary of the three-layer architecture
2. The four required-reading files from `CLAUDE.md`
3. The three skills with their trigger conditions

If the agent skips any of these, the configuration is not yet effective.
Fix it before any ingest is attempted.

---

## First ingest session

After confirming the configuration, start the first real ingest:

> Read AGENTS.md, CLAUDE.md, .claude/skills/primary-source-ingest/SKILL.md,
> and .claude/skills/legal-citation-verifier/SKILL.md. Then ingest
> raw_sources/acts/central_tpa_1882.pdf, focusing on Section 106.
> Propose a PR per the ingest protocol. Do not merge.

This session is where the Karpathy LLM-Wiki pattern proves itself: the agent
reads the source, verifies citations, proposes a wiki article, and opens a PR
— all without ever committing to `main` or fabricating a citation.

---

## Why this matters for a legal project

The failure mode in legal-information AI is silent fabrication: a model
confidently states a court fee, notice period, or procedural step that is
wrong. The three-layer design addresses this specifically:

- **Skills are mandatory reads**, not optional enhancement. An agent that
  skips the citation verifier skill is an unconfigured agent.
- **`raw_sources/` is immutable.** Nothing is ever modified there. The
  citation chain always traces to an unmodified source file.
- **Human merge gate.** Every wiki change goes through a PR that a human
  reviews and merges. The agent proposes; the human decides.
- **Status tiers.** Articles are `unreviewed-primary-sources-only` until a
  qualified legal reviewer signs off. Users always see the status.
