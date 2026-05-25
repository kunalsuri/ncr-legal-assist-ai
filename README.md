# Delhi-NCR-Legal-Assist-AI

A retrieval-augmented research system over Indian legal primary sources
(statutes, rules, court forms) for the Delhi NCR jurisdiction, scoped to
property, tenancy, and housing law.

> ⚠️ **This is a technical research project, not a legal information service.**
> See [DISCLAIMER.md](./DISCLAIMER.md) before using or extending this code.

[![License: Apache 2.0](https://img.shields.io/badge/code-Apache%202.0-blue.svg)](./LICENSE)
[![KB License: CC-BY-SA-4.0](https://img.shields.io/badge/kb-CC--BY--SA--4.0-lightgrey.svg)](./knowledge_base/)
[![Status: Pre-alpha](https://img.shields.io/badge/status-pre--alpha-orange.svg)](./README.md#project-status)

## What this is

- An open-source software scaffold demonstrating retrieval-augmented
  generation (RAG) over publicly available Indian legal texts.
- A reproducible local pipeline using open-weights language models, hybrid
  retrieval (BM25 + dense embeddings + cross-encoder reranking), and strict
  citation verification.
- A scaffold for community-contributed, expert-reviewed knowledge-base
  articles. **No articles in this repository are currently expert-reviewed.**
  Every knowledge-base file carries `status: unreviewed-primary-sources-only`
  in its frontmatter until a qualified reviewer signs off.

## What this is NOT

- Not legal advice.
- Not a substitute for consulting a qualified advocate enrolled with a State
  Bar Council under the Advocates Act, 1961.
- Not a service offered to the public; it is source code that a technically
  capable user can run locally for research and educational purposes.
- Not affiliated with any court, bar council, government body, or law firm.

## Scope (v1)

Five seed topics in Delhi tenancy, RERA, and property law. Statutes, rules,
and court forms only. English only. No case law in v1. No Hindi in v1.

## Repository layout

This project follows the **Karpathy LLM-Wiki pattern** adapted for a legal
domain — three immutable layers with strict boundaries:

```
ncr-legal-assist-ai/
├── raw_sources/          # Immutable primary legal documents (PDFs, CSV, XLSX)
│                         # Agents: read-only. Humans: add only.
├── knowledge_base/       # Wiki articles paraphrasing raw_sources/ with citations
│   ├── index.md          # Catalog of all articles
│   ├── SCHEMA.md         # Required frontmatter schema
│   └── statutes/         # Statute-by-statute paraphrase articles
├── src/                  # RAG query layer (retrieval + generation + app)
│   ├── app/              # Streamlit UI
│   ├── generation/       # LLM client, prompts, citation verifier
│   ├── indexing/         # Embeddings and vector store
│   ├── ingestion/        # Chunker and Markdown loader
│   └── retrieval/        # Hybrid retriever and reranker
├── tests/                # pytest test suite (must pass before any PR)
├── scripts/              # Index builder and model downloader
├── specs/                # Technical specification
├── docs/                 # Extended documentation
├── AGENTS.md             # Authoritative AI agent schema (read this first)
├── CLAUDE.md             # Claude Code entry point → defers to AGENTS.md
└── .github/
    └── copilot-instructions.md  # Copilot entry point → defers to AGENTS.md
```

The `raw_sources/` layer is never modified by agents or automation. The
`knowledge_base/` layer is maintained by AI agents under human-merged PRs.
The `src/` layer is the runtime query engine.

For details on the agent configuration, see [docs/agent-configuration.md](./docs/agent-configuration.md).

## Architecture

```
User (Streamlit UI)
    ↓
Intent classifier (keyword + heuristic; LLM-based in v2)
    ↓
Hybrid Retriever
    ├── BM25 (rank_bm25)
    ├── Dense (InLegalBERT embeddings → Qdrant)
    └── Reranker (BAAI/bge-reranker-v2-m3)
    ↓
Confidence gate (rerank score ≥ threshold or refuse)
    ↓
LLM generation (Qwen3-8B-Instruct or Llama-3.3-8B-Instruct, served via vLLM)
    with strict system prompt: cite-or-refuse
    ↓
Citation verifier (regex-extract citations, check against retrieved sources)
    ↓
Streamlit response with sources panel
```

## Models used (all open-weights, downloaded locally)

| Purpose                | Model                                | Source       |
|------------------------|--------------------------------------|--------------|
| Generation             | `Qwen/Qwen3-8B-Instruct` (AWQ)       | Hugging Face |
| English legal embeds   | `law-ai/InLegalBERT`                 | Hugging Face |
| Reranker               | `BAAI/bge-reranker-v2-m3`            | Hugging Face |

Alternative generation models (configurable in `.env`):
`meta-llama/Llama-3.3-8B-Instruct`, `mistralai/Mistral-Small-Instruct-2409`.

## Primary data sources

All knowledge-base articles must cite only from these public, authoritative
sources. No secondary or interpretive sources may be used as primary citations.

- **India Code** (`indiacode.nic.in`) — consolidated central Acts
- **Delhi Government Legislative Department** — Delhi-specific Acts
- **e-Gazette** (`egazette.nic.in`) — rules and notifications
- **Delhi High Court** (`delhihighcourt.nic.in`) — court rules and forms
- **NJDG** (`njdg.ecourts.gov.in`) — procedural statistics
- **Ministry of Law and Justice** — canonical statutory text

See [`knowledge_base/SCHEMA.md`](./knowledge_base/SCHEMA.md) for required
frontmatter format.

## Quick start

```bash
git clone https://github.com/<your-username>/delhi-legal-assist.git
cd delhi-legal-assist

# Set up Git LFS (required for raw_sources/ binaries)
git lfs install
git lfs pull

cp .env.example .env
make install
make download-models
make build-index
make serve-llm        # in one terminal
make run-app          # in another terminal
```

## Project status

**Pre-alpha.** Five knowledge-base article stubs exist (frontmatter only,
no body content). No reviewer is engaged. The pipeline runs end-to-end on
an empty knowledge base. See [`knowledge_base/index.md`](./knowledge_base/index.md)
for the current article list.

## AI agent configuration

This repository is configured for use with Claude Code and GitHub Copilot
as disciplined wiki librarians. The configuration uses a three-layer design:

1. **[`AGENTS.md`](./AGENTS.md)** — authoritative schema. Read this first.
2. **[`CLAUDE.md`](./CLAUDE.md)** / **[`.github/copilot-instructions.md`](./.github/copilot-instructions.md)** — thin tool-specific pointers to `AGENTS.md`.
3. **`.claude/skills/`** — three mandatory operational playbooks:
   - `legal-citation-verifier` — before writing any wiki content
   - `primary-source-ingest` — when ingesting a `raw_sources/` document
   - `wiki-lint` — when running a wiki health check

See [docs/agent-configuration.md](./docs/agent-configuration.md) for the full
setup guide, Git LFS configuration, and first-session verification steps.

## Roadmap

- **v0.1** (this scaffold): empty KB, working pipeline, refusal path
- **v0.2**: five seed articles written from primary sources, unreviewed
- **v0.3**: first expert-reviewed article
- **v0.4**: Hindi translation pipeline
- **v0.5**: judgment corpus integration (Indian Kanoon API)
- **v1.0**: ten expert-reviewed articles, Hindi support, public demo

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Pull requests adding knowledge-base
articles must cite only primary sources and will not be merged without
review by a qualified legal reviewer.

## License

- **Code**: Apache License 2.0 (see [LICENSE](./LICENSE))
- **Knowledge-base content** (Markdown files under `knowledge_base/`):
  Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA-4.0)

## Acknowledgements

This project draws on the open-source work of:
- **OpenNyAI** (`opennyai.org`) — Aalap model, InJudgements dataset
- **Law-AI group, IIT Kharagpur** — InLegalBERT
- **Nyaaya / Vidhi Centre for Legal Policy** — plain-language legal information
- **Daksh India** — empirical judicial data
- **Agami** — legal-AI community

Their work is the precondition for this project.

## Disclaimer

See [DISCLAIMER.md](./DISCLAIMER.md). Read it before running this code or
extending it.
