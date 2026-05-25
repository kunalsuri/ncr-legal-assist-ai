# Delhi-NCR-Legal-Assist-AI

A retrieval-augmented research system over Indian legal primary sources
(statutes, rules, court forms) for the Delhi NCR jurisdiction, scoped to
property, tenancy, and housing law.

> ⚠️ **This is a technical research project, not a legal information service.**
> See [DISCLAIMER.md](./DISCLAIMER.md) before using or extending this code.

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
cp .env.example .env
make install
make download-models
make build-index
make serve-llm        # in one terminal
make run-app          # in another terminal
```

## Project status

**Pre-alpha.** No knowledge-base articles are written. No reviewer is engaged.
The pipeline runs end-to-end on an empty knowledge base.

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
