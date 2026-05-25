# Specification: `delhi-legal-assist` — Repository Scaffold

This document is a build specification for an AI coding agent (GitHub Copilot
or equivalent). Follow it literally. Do not add features beyond what is
specified. Do not generate legal content; only generate the repository
structure, configuration files, code skeletons, and documentation described
here. Placeholder content where indicated must remain placeholder content.

---

## 1. Project goal (for the agent's context, not for invention)

A self-hosted, open-source retrieval system over public Indian legal primary
sources (statutes, rules, court forms) for the Delhi NCR jurisdiction, focused
on property, tenancy, and housing law. The system uses local open-weights LLMs
and a Streamlit frontend. It is published under Apache-2.0 as a technical
research project, not as a legal information service.

The agent must not invent legal content, statute text, case citations, or
procedural information. All knowledge-base files in this scaffold are empty
templates with frontmatter only.

---

## 2. Repository metadata

- **Repository name**: `delhi-legal-assist`
- **License**: Apache License 2.0 (include full text in `LICENSE`)
- **Knowledge-base content license**: CC-BY-SA-4.0 (declared in README;
  no separate file needed at this stage)
- **Default branch**: `main`
- **Python version**: 3.11
- **Visibility**: public

---

## 3. Directory structure to create

Create exactly this structure. Files marked `[skeleton]` get the code
skeleton specified in Section 6. Files marked `[empty template]` get only
YAML frontmatter as specified in Section 5. Files marked `[full]` get the
complete content specified in the corresponding section.

```
delhi-legal-assist/
├── LICENSE                                    [full — Apache 2.0 text]
├── README.md                                  [full — see Section 4]
├── DISCLAIMER.md                              [full — see Section 4.2]
├── CONTRIBUTING.md                            [full — see Section 4.3]
├── CODE_OF_CONDUCT.md                         [full — Contributor Covenant 2.1]
├── SECURITY.md                                [full — see Section 4.4]
├── .gitignore                                 [full — Python + data dirs]
├── .env.example                               [full — see Section 6.1]
├── pyproject.toml                             [full — see Section 6.2]
├── docker-compose.yml                         [full — see Section 6.3]
├── Makefile                                   [full — see Section 6.4]
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── kb_article_review.md               [full — see Section 4.5]
│   │   ├── bug_report.md                      [full]
│   │   └── factual_correction.md              [full — see Section 4.5]
│   ├── PULL_REQUEST_TEMPLATE.md               [full — see Section 4.6]
│   └── workflows/
│       └── ci.yml                             [full — lint + test only]
│
├── knowledge_base/
│   ├── README.md                              [full — see Section 5.1]
│   ├── SCHEMA.md                              [full — see Section 5.2]
│   └── statutes/
│       ├── dl-tenancy-deposit-recovery.md     [empty template — Section 5.3]
│       ├── dl-tenancy-section-106-notice.md   [empty template]
│       ├── dl-tenancy-rent-agreement.md       [empty template]
│       ├── dl-rera-complaint-filing.md        [empty template]
│       └── dl-property-mutation.md            [empty template]
│
├── data/
│   └── .gitkeep                               [empty file; dir is gitignored]
│
├── src/
│   ├── __init__.py                            [empty]
│   ├── config.py                              [skeleton — Section 6.5]
│   ├── ingestion/
│   │   ├── __init__.py                        [empty]
│   │   ├── markdown_loader.py                 [skeleton — Section 6.6]
│   │   └── chunker.py                         [skeleton — Section 6.7]
│   ├── indexing/
│   │   ├── __init__.py                        [empty]
│   │   ├── embeddings.py                      [skeleton — Section 6.8]
│   │   └── vector_store.py                    [skeleton — Section 6.9]
│   ├── retrieval/
│   │   ├── __init__.py                        [empty]
│   │   ├── hybrid_retriever.py                [skeleton — Section 6.10]
│   │   └── reranker.py                        [skeleton — Section 6.11]
│   ├── generation/
│   │   ├── __init__.py                        [empty]
│   │   ├── llm_client.py                      [skeleton — Section 6.12]
│   │   ├── prompts.py                         [skeleton — Section 6.13]
│   │   └── verifier.py                        [skeleton — Section 6.14]
│   └── app/
│       ├── __init__.py                        [empty]
│       └── streamlit_app.py                   [skeleton — Section 6.15]
│
├── scripts/
│   ├── download_models.py                     [skeleton — Section 6.16]
│   └── build_index.py                         [skeleton — Section 6.17]
│
└── tests/
    ├── __init__.py                            [empty]
    ├── test_markdown_loader.py                [skeleton — Section 6.18]
    ├── test_verifier.py                       [skeleton — Section 6.19]
    └── test_refusal.py                        [skeleton — Section 6.20]
```

---

## 4. Top-level documentation files

### 4.1 `README.md` (full content to generate)

````markdown
# delhi-legal-assist

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
````

### 4.2 `DISCLAIMER.md` (full content to generate)

```markdown
# Disclaimer

## Nature of this project

`delhi-legal-assist` is open-source software published for research,
educational, and technical demonstration purposes. It is not a legal service,
legal information service, or substitute for legal counsel.

## Not legal advice

Nothing produced by this software constitutes legal advice. Output from this
software is the result of a retrieval-augmented language model operating over
publicly available statutory texts. The output may be incomplete, outdated,
or incorrect. No advocate–client relationship is created by the use of this
software.

## Not a practising lawyer

This software is not a practising advocate. Under the Advocates Act, 1961
(particularly Sections 29, 32, and 33), the practice of law in India is
restricted to advocates enrolled with a State Bar Council. This software does
not practise law, does not represent any party, and does not appear before
any court, tribunal, or authority.

## Information vs. advice

This software is designed to surface information about what statutes, rules,
and court forms say. It is not designed to apply that information to any
user's specific facts or circumstances. The application of law to facts is
the work of a qualified advocate.

## Accuracy

While the system is designed to refuse to answer when retrieval confidence
is low, and to verify that all citations in generated output correspond to
retrieved sources, the system can still produce errors. Users must
independently verify any information against the cited primary source before
relying on it for any purpose.

## No reviewer

As of this release, no knowledge-base article in this repository has been
reviewed by a qualified legal reviewer. All articles carry the frontmatter
status `unreviewed-primary-sources-only`. Articles are paraphrases of
primary statutory text with citations, written by non-lawyers.

## Use at your own risk

This software is provided "AS IS", without warranty of any kind, express or
implied, as set out in the Apache License 2.0. The authors and contributors
disclaim all liability arising from use of this software.

## If you have a legal problem

If you have an actual legal problem relating to property, tenancy, or
housing in Delhi NCR, consult:

- **Delhi State Legal Services Authority (DSLSA)** — Helpline: **1516**
- **Delhi High Court Legal Services Committee (DHCLSC)** — for matters before
  the Delhi High Court
- **NALSA** (National Legal Services Authority) — `nalsa.gov.in`
- A qualified advocate enrolled with the Bar Council of Delhi
- Free legal information at **Nyaaya** (`nyaaya.org`)
- Legal aid clinics at NLU Delhi, Faculty of Law DU, and Jindal Global Law School

## Jurisdiction

This software is developed in India and scoped to Delhi NCR law. Users
outside this jurisdiction should not rely on its output.

## Contact

Issues and corrections: open a GitHub issue using the
`factual_correction` template.
```

### 4.3 `CONTRIBUTING.md` (full content to generate)

```markdown
# Contributing

Thank you for considering a contribution. This project has unusual rules
because of its subject matter. Please read them before opening an issue or
pull request.

## Three kinds of contributions

### 1. Code contributions

Standard open-source process. Open a PR against `main` with tests. The CI
must pass. Follow PEP 8 and the existing style.

### 2. Knowledge-base article contributions

This is the contribution we most need and the one with the strictest rules.

**Primary-source rule.** Every factual sentence in a knowledge-base article
must be traceable to a specific section of a specific statute, a specific
rule, a specific court form, or a specific government publication. If you
cannot cite a primary source by section number or paragraph, the sentence
does not go in.

**Permitted primary sources** are listed in
[`knowledge_base/README.md`](./knowledge_base/README.md).

**Secondary sources** (Nyaaya, Daksh, HLRN, DSLSA handbooks, law firm
publications, academic articles) may be consulted to verify your reading of
primary sources, and listed under `secondary_sources_consulted` in the
frontmatter, but they may not be the basis of factual claims.

**No interpretation.** Do not write "this means" or "the courts have held"
or "in practice." Write only what the statute says, in plain language,
section by section.

**Frontmatter.** Every article must conform to the schema in
[`knowledge_base/SCHEMA.md`](./knowledge_base/SCHEMA.md). Articles without
valid frontmatter will not be merged.

**Review status.** New articles are merged with
`status: unreviewed-primary-sources-only`. They are promoted to
`status: reviewed` only after a qualified reviewer (an advocate enrolled
with a State Bar Council, or a law faculty member at a recognised law school)
signs off via the `kb_article_review` issue template.

### 3. Review contributions

If you are a qualified legal reviewer willing to review one or more articles,
please open an issue using the `kb_article_review` template. We will credit
you in the article frontmatter and in the README acknowledgements.

## What we do not accept

- Pull requests with unsourced legal claims
- Pull requests that add interpretive or advisory content
- Pull requests outside the Delhi NCR property/tenancy/housing scope
  (until v2)
- Pull requests adding case-law analysis (until the judgment corpus is
  integrated in v0.5)

## Code of conduct

See [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md). Contributor Covenant 2.1
applies.
```

### 4.4 `SECURITY.md` (full content to generate)

```markdown
# Security Policy

## Reporting a vulnerability

Open a private security advisory on GitHub, or email the maintainer listed
in the repository profile. Do not open a public issue for security
vulnerabilities.

## Scope

This project runs locally and processes only publicly available legal texts.
It does not collect user data. If you find a vulnerability that could cause:

- Leakage of any local data to external services
- Execution of untrusted content from the knowledge base
- Bypass of the citation verifier or refusal path

please report it as above.

## Out of scope

- Hallucinated output from the language model (this is a known limitation
  mitigated by the citation verifier; report via a regular issue with the
  `factual_correction` template).
- Performance or model-quality issues.
```

### 4.5 Issue templates

`kb_article_review.md`:

```markdown
---
name: Knowledge-base article review
about: For qualified legal reviewers signing off on a KB article
title: "[REVIEW] <article-id>"
labels: review
---

**Article ID**: <e.g. dl-tenancy-deposit-recovery>
**Article path**: <e.g. knowledge_base/statutes/dl-tenancy-deposit-recovery.md>

**Reviewer name**:
**Bar Council enrolment number (if applicable)**:
**Institutional affiliation (if applicable)**:

**Review outcome**: [ ] Approved as-is  [ ] Approved with changes  [ ] Rejected

**Comments / required changes**:

**Sections of the article reviewed**:

**Date of review**:

By submitting this review, I confirm that I have reviewed the article
against the cited primary sources and that the article accurately
paraphrases those sources without legal interpretation.
```

`factual_correction.md`:

```markdown
---
name: Factual correction
about: Report an inaccuracy in a knowledge-base article or system output
title: "[CORRECTION] <brief description>"
labels: correction
---

**Article ID or query that produced the inaccuracy**:

**What the article or system said**:

**What the correct information is**:

**Primary source supporting your correction** (statute section, rule, form):

**Additional context**:
```

### 4.6 `PULL_REQUEST_TEMPLATE.md`

```markdown
## What this PR does

## Type of change
- [ ] Code change (bug fix, feature, refactor)
- [ ] Knowledge-base article (new or updated)
- [ ] Documentation
- [ ] CI / tooling

## For knowledge-base PRs only
- [ ] Every factual claim cites a primary source by section/paragraph
- [ ] Frontmatter conforms to `knowledge_base/SCHEMA.md`
- [ ] `status` is set to `unreviewed-primary-sources-only`
- [ ] No interpretive or advisory language
- [ ] Secondary sources (if consulted) are listed under
      `secondary_sources_consulted`

## For code PRs only
- [ ] Tests added or updated
- [ ] `make lint` passes
- [ ] `make test` passes

## Related issues
Closes #
```

---

## 5. Knowledge-base scaffolding

### 5.1 `knowledge_base/README.md` (full content)

```markdown
# Knowledge Base

This directory contains the Markdown knowledge base over which the retrieval
system operates.

## Rules

1. Every article must have valid frontmatter per [SCHEMA.md](./SCHEMA.md).
2. Every factual sentence must cite a primary source.
3. No interpretation, no advice, no case-law analysis (until v0.5).
4. New articles are merged with `status: unreviewed-primary-sources-only`.

## Permitted primary sources

- **India Code**: https://www.indiacode.nic.in/
- **Delhi Government Legislative Department**
- **e-Gazette of India**: https://egazette.gov.in/
- **Delhi High Court**: https://delhihighcourt.nic.in/
- **National Judicial Data Grid**: https://njdg.ecourts.gov.in/
- **Ministry of Law and Justice publications**
- **Statutory authority publications** (DSLSA, DHCLSC, Delhi RERA, DDA)

## File naming

`<jurisdiction>-<topic>-<subtopic>.md` in lowercase, hyphenated.
Examples: `dl-tenancy-deposit-recovery.md`, `dl-rera-complaint-filing.md`.

## Article structure

Articles should be organised by statute section, not by user question.
Each section heading paraphrases the corresponding statutory provision and
cites it.
```

### 5.2 `knowledge_base/SCHEMA.md` (full content)

````markdown
# Knowledge-base article schema

Every Markdown file under `knowledge_base/` must begin with YAML frontmatter
conforming to the schema below.

## Required fields

```yaml
---
id: string                          # unique slug, matches filename without .md
title: string                       # human-readable title
status: string                      # one of: unreviewed-primary-sources-only, reviewed, deprecated
jurisdiction: list[string]          # e.g. [Delhi]
topic: string                       # one of: tenancy, property, rera, housing, mutation
audience: string                    # one of: tenant, buyer, seller, paralegal, lawyer, any
language: string                    # en | hi
primary_sources:
  - act: string                     # full Act name with year
    sections: list[string]          # e.g. ["106", "108(q)"]
    url: string                     # link to India Code or official source
secondary_sources_consulted: list[string]   # may be empty
last_reviewed: string | null        # ISO date or null
reviewer: string | null             # reviewer name or null
disclaimer_level: string            # one of: high, standard
---
```

## Example

```yaml
---
id: dl-tenancy-deposit-recovery
title: Security deposit recovery under Delhi tenancy law
status: unreviewed-primary-sources-only
jurisdiction: [Delhi]
topic: tenancy
audience: tenant
language: en
primary_sources:
  - act: "Transfer of Property Act, 1882"
    sections: ["108"]
    url: "https://www.indiacode.nic.in/handle/123456789/2338"
  - act: "Delhi Rent Control Act, 1958"
    sections: ["27"]
    url: "https://www.indiacode.nic.in/..."
secondary_sources_consulted: []
last_reviewed: null
reviewer: null
disclaimer_level: high
---
```
````

### 5.3 Empty article templates

Each of the five seed article files under `knowledge_base/statutes/` must be
created with only the frontmatter below and a single placeholder body line.
The agent must not invent statutory content.

Template for `dl-tenancy-deposit-recovery.md`:

```markdown
---
id: dl-tenancy-deposit-recovery
title: Security deposit recovery under Delhi tenancy law
status: unreviewed-primary-sources-only
jurisdiction: [Delhi]
topic: tenancy
audience: tenant
language: en
primary_sources: []
secondary_sources_consulted: []
last_reviewed: null
reviewer: null
disclaimer_level: high
---

<!-- TODO: Author content. Every sentence must cite a primary source.
     See knowledge_base/README.md for permitted sources and rules. -->
```

Use the same template, changing only the `id`, `title`, `topic`, and
`audience` fields, for the remaining four files:

- `dl-tenancy-section-106-notice.md` — title: "Section 106 TPA notice
  requirements", topic: `tenancy`, audience: `any`
- `dl-tenancy-rent-agreement.md` — title: "Rent agreement registration in
  Delhi", topic: `tenancy`, audience: `any`
- `dl-rera-complaint-filing.md` — title: "Filing a complaint with Delhi
  RERA", topic: `rera`, audience: `buyer`
- `dl-property-mutation.md` — title: "Property mutation procedure in Delhi",
  topic: `mutation`, audience: `any`

---

## 6. Code skeletons

### 6.1 `.env.example`

```env
# LLM
LLM_ENDPOINT=http://localhost:8000/v1
LLM_MODEL=Qwen/Qwen3-8B-Instruct-AWQ
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1024

# Embeddings
EMBEDDING_MODEL=law-ai/InLegalBERT
RERANKER_MODEL=BAAI/bge-reranker-v2-m3

# Vector store
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=delhi_legal_kb

# Retrieval
TOP_K=8
RERANK_CONFIDENCE_THRESHOLD=0.55

# Paths
KB_ROOT=./knowledge_base
DATA_ROOT=./data
```

### 6.2 `pyproject.toml`

```toml
[project]
name = "delhi-legal-assist"
version = "0.1.0"
description = "Research RAG system over Indian legal primary sources for Delhi NCR"
readme = "README.md"
license = { text = "Apache-2.0" }
requires-python = ">=3.11"
dependencies = [
    "streamlit>=1.40",
    "transformers>=4.45",
    "sentence-transformers>=3.0",
    "torch>=2.4",
    "qdrant-client>=1.12",
    "rank-bm25>=0.2.2",
    "FlagEmbedding>=1.3",
    "pydantic>=2.9",
    "pyyaml>=6.0",
    "python-frontmatter>=1.1",
    "python-dotenv>=1.0",
    "openai>=1.50",   # used as a client against the local vLLM server
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3",
    "ruff>=0.6",
    "mypy>=1.11",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 6.3 `docker-compose.yml`

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - ./data/qdrant:/qdrant/storage
```

### 6.4 `Makefile`

```makefile
.PHONY: install download-models build-index serve-llm run-app lint test

install:
	pip install -e ".[dev]"

download-models:
	python scripts/download_models.py

build-index:
	docker compose up -d qdrant
	python scripts/build_index.py

serve-llm:
	@echo "Start vLLM server manually, e.g.:"
	@echo "  vllm serve Qwen/Qwen3-8B-Instruct-AWQ --port 8000 --quantization awq"

run-app:
	streamlit run src/app/streamlit_app.py

lint:
	ruff check src tests scripts

test:
	pytest -v
```

### 6.5 `src/config.py`

```python
"""Configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    llm_endpoint: str
    llm_model: str
    llm_temperature: float
    llm_max_tokens: int
    embedding_model: str
    reranker_model: str
    qdrant_host: str
    qdrant_port: int
    qdrant_collection: str
    top_k: int
    rerank_confidence_threshold: float
    kb_root: Path
    data_root: Path


def load_config() -> Config:
    return Config(
        llm_endpoint=os.environ["LLM_ENDPOINT"],
        llm_model=os.environ["LLM_MODEL"],
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
        embedding_model=os.environ["EMBEDDING_MODEL"],
        reranker_model=os.environ["RERANKER_MODEL"],
        qdrant_host=os.environ["QDRANT_HOST"],
        qdrant_port=int(os.environ["QDRANT_PORT"]),
        qdrant_collection=os.environ["QDRANT_COLLECTION"],
        top_k=int(os.getenv("TOP_K", "8")),
        rerank_confidence_threshold=float(
            os.getenv("RERANK_CONFIDENCE_THRESHOLD", "0.55")
        ),
        kb_root=Path(os.environ["KB_ROOT"]),
        data_root=Path(os.environ["DATA_ROOT"]),
    )
```

### 6.6 `src/ingestion/markdown_loader.py`

```python
"""Load Markdown KB files with YAML frontmatter into typed records."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import frontmatter
from pydantic import BaseModel, Field


class PrimarySource(BaseModel):
    act: str
    sections: list[str]
    url: str


class KBArticle(BaseModel):
    id: str
    title: str
    status: Literal["unreviewed-primary-sources-only", "reviewed", "deprecated"]
    jurisdiction: list[str]
    topic: str
    audience: str
    language: Literal["en", "hi"]
    primary_sources: list[PrimarySource] = Field(default_factory=list)
    secondary_sources_consulted: list[str] = Field(default_factory=list)
    last_reviewed: str | None = None
    reviewer: str | None = None
    disclaimer_level: Literal["high", "standard"] = "high"
    body: str
    source_path: str


def load_kb(kb_root: Path) -> list[KBArticle]:
    """Walk kb_root and return all valid articles. Skip files with empty bodies."""
    articles: list[KBArticle] = []
    for md_path in kb_root.rglob("*.md"):
        if md_path.name in {"README.md", "SCHEMA.md"}:
            continue
        post = frontmatter.load(md_path)
        if not post.content.strip() or post.content.strip().startswith("<!--"):
            continue  # skip empty template files
        article = KBArticle(
            **post.metadata,
            body=post.content,
            source_path=str(md_path.relative_to(kb_root)),
        )
        articles.append(article)
    return articles
```

### 6.7 `src/ingestion/chunker.py`

```python
"""Split KB articles into retrievable chunks at heading boundaries."""
from __future__ import annotations

import re
from pydantic import BaseModel

from src.ingestion.markdown_loader import KBArticle


class Chunk(BaseModel):
    chunk_id: str
    article_id: str
    source_path: str
    heading_path: list[str]
    text: str
    article_status: str
    article_title: str


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def chunk_article(article: KBArticle) -> list[Chunk]:
    """Split on Markdown headings. Each heading section becomes one chunk."""
    chunks: list[Chunk] = []
    sections = _split_by_heading(article.body)
    for i, (heading_path, text) in enumerate(sections):
        if not text.strip():
            continue
        chunks.append(Chunk(
            chunk_id=f"{article.id}#{i:03d}",
            article_id=article.id,
            source_path=article.source_path,
            heading_path=heading_path,
            text=text.strip(),
            article_status=article.status,
            article_title=article.title,
        ))
    return chunks


def _split_by_heading(body: str) -> list[tuple[list[str], str]]:
    """Return [(heading_path, body_text)] pairs."""
    # Simple implementation: split by top-level headings; ignore deeper nesting in v1.
    parts: list[tuple[list[str], str]] = []
    current_heading: list[str] = []
    current_text: list[str] = []
    for line in body.splitlines():
        m = HEADING_RE.match(line)
        if m:
            if current_text:
                parts.append((current_heading, "\n".join(current_text)))
                current_text = []
            current_heading = [m.group(2).strip()]
        else:
            current_text.append(line)
    if current_text:
        parts.append((current_heading, "\n".join(current_text)))
    return parts
```

### 6.8 `src/indexing/embeddings.py`

```python
"""Wrap an embedding model. v1 uses sentence-transformers with InLegalBERT."""
from __future__ import annotations

from sentence_transformers import SentenceTransformer
import numpy as np


class Embedder:
    def __init__(self, model_name: str) -> None:
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True)

    @property
    def dim(self) -> int:
        return self.model.get_sentence_embedding_dimension()
```

### 6.9 `src/indexing/vector_store.py`

```python
"""Qdrant wrapper for the KB collection."""
from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from src.ingestion.chunker import Chunk


class VectorStore:
    def __init__(self, host: str, port: int, collection: str, dim: int) -> None:
        self.client = QdrantClient(host=host, port=port)
        self.collection = collection
        self._ensure_collection(dim)

    def _ensure_collection(self, dim: int) -> None:
        existing = {c.name for c in self.client.get_collections().collections}
        if self.collection not in existing:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=qm.VectorParams(size=dim, distance=qm.Distance.COSINE),
            )

    def upsert(self, chunks: list[Chunk], vectors) -> None:
        points = [
            qm.PointStruct(
                id=i,
                vector=vec.tolist(),
                payload={
                    "chunk_id": c.chunk_id,
                    "article_id": c.article_id,
                    "source_path": c.source_path,
                    "heading_path": c.heading_path,
                    "text": c.text,
                    "article_status": c.article_status,
                    "article_title": c.article_title,
                },
            )
            for i, (c, vec) in enumerate(zip(chunks, vectors))
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query_vec, limit: int) -> list[dict]:
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=query_vec.tolist(),
            limit=limit,
        )
        return [h.payload | {"score": h.score} for h in hits]
```

### 6.10 `src/retrieval/hybrid_retriever.py`

```python
"""BM25 + dense retrieval with reranking and a confidence gate."""
from __future__ import annotations

from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from src.indexing.embeddings import Embedder
from src.indexing.vector_store import VectorStore
from src.retrieval.reranker import Reranker


@dataclass
class RetrievalResult:
    chunk_id: str
    article_id: str
    source_path: str
    heading_path: list[str]
    text: str
    article_status: str
    article_title: str
    rerank_score: float


class HybridRetriever:
    def __init__(
        self,
        vector_store: VectorStore,
        embedder: Embedder,
        reranker: Reranker,
        bm25: BM25Okapi,
        chunks_by_id: dict,
        confidence_threshold: float,
    ) -> None:
        self.vector_store = vector_store
        self.embedder = embedder
        self.reranker = reranker
        self.bm25 = bm25
        self.chunks_by_id = chunks_by_id
        self.confidence_threshold = confidence_threshold

    def retrieve(self, query: str, k: int = 8) -> tuple[list[RetrievalResult], bool]:
        q_vec = self.embedder.encode([query])[0]
        dense_hits = self.vector_store.search(q_vec, limit=k * 3)
        dense_ids = {h["chunk_id"] for h in dense_hits}

        bm25_scores = self.bm25.get_scores(query.lower().split())
        ranked_ids = [cid for cid, _ in sorted(
            zip(self.chunks_by_id.keys(), bm25_scores),
            key=lambda x: -x[1],
        )[: k * 3]]
        candidate_ids = list(dense_ids | set(ranked_ids))

        pairs = [(query, self.chunks_by_id[cid].text) for cid in candidate_ids]
        scores = self.reranker.score(pairs)
        ranked = sorted(zip(candidate_ids, scores), key=lambda x: -x[1])[:k]

        results = [
            RetrievalResult(
                chunk_id=cid,
                article_id=self.chunks_by_id[cid].article_id,
                source_path=self.chunks_by_id[cid].source_path,
                heading_path=self.chunks_by_id[cid].heading_path,
                text=self.chunks_by_id[cid].text,
                article_status=self.chunks_by_id[cid].article_status,
                article_title=self.chunks_by_id[cid].article_title,
                rerank_score=float(score),
            )
            for cid, score in ranked
        ]
        confident = bool(results) and results[0].rerank_score >= self.confidence_threshold
        return results, confident
```

### 6.11 `src/retrieval/reranker.py`

```python
"""Cross-encoder reranker."""
from __future__ import annotations

from FlagEmbedding import FlagReranker


class Reranker:
    def __init__(self, model_name: str) -> None:
        self.model = FlagReranker(model_name, use_fp16=True)

    def score(self, pairs: list[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        scores = self.model.compute_score([list(p) for p in pairs], normalize=True)
        if isinstance(scores, float):
            return [scores]
        return list(scores)
```

### 6.12 `src/generation/llm_client.py`

```python
"""Client for a local OpenAI-compatible LLM server (vLLM, llama.cpp server)."""
from __future__ import annotations

from openai import OpenAI


class LLMClient:
    def __init__(self, endpoint: str, model: str, temperature: float, max_tokens: int) -> None:
        self.client = OpenAI(base_url=endpoint, api_key="not-needed")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or ""
```

### 6.13 `src/generation/prompts.py`

```python
"""System and user prompt templates. Strict cite-or-refuse."""

SYSTEM_PROMPT = """You are an information retrieval assistant for a research
project on Delhi NCR property and tenancy law. You are NOT a lawyer and you
do NOT give legal advice.

STRICT RULES:
1. Answer ONLY from the provided <sources>. If the sources do not contain
   the answer, reply exactly:
   "I cannot verify this from my sources. Please consult the Delhi State
   Legal Services Authority helpline (1516) or Nyaaya (nyaaya.org)."
2. Every factual claim must end with a citation in the format
   [article_id, heading]. Multiple citations allowed.
3. Never invent statute sections, court fees, timelines, or case names.
4. If asked for advice on a specific situation, reply with the relevant
   information from sources and append:
   "This is information about what the law says, not advice on your specific
   case. Consult a qualified advocate."
5. If the article_status of any source is 'unreviewed-primary-sources-only',
   prepend the reply with:
   "[Unreviewed sources] The information below is paraphrased from primary
   statutory text but has not been reviewed by a qualified lawyer."
6. Reply in plain English, short sentences, no legalese except direct
   statutory quotations.
"""


USER_TEMPLATE = """<query>
{query}
</query>

<sources>
{formatted_sources}
</sources>
"""


REFUSAL_MESSAGE = """I cannot answer this confidently from my current
knowledge base.

For matters of Delhi NCR property, tenancy, or housing law, please consult:
- Delhi State Legal Services Authority — helpline 1516
- Nyaaya (free legal information) — nyaaya.org
- A qualified advocate enrolled with the Bar Council of Delhi
"""


def format_sources(results) -> str:
    parts = []
    for r in results:
        heading = " > ".join(r.heading_path) if r.heading_path else "(top)"
        parts.append(
            f"[{r.article_id}, {heading}] (status: {r.article_status})\n"
            f"From: {r.source_path}\n\n{r.text}"
        )
    return "\n\n---\n\n".join(parts)
```

### 6.14 `src/generation/verifier.py`

```python
"""Post-hoc citation verification. Any answer with a fabricated citation is suppressed."""
from __future__ import annotations

import re

CITATION_PATTERN = re.compile(r"\[([a-z0-9\-]+)(?:,\s*[^\]]+)?\]")


def verify_answer(answer: str, retrieved_article_ids: set[str]) -> tuple[bool, list[str]]:
    """Return (is_valid, list_of_fabricated_ids).

    Valid means: at least one citation is present AND every cited article_id
    appears in the retrieved set.
    """
    cited = set(CITATION_PATTERN.findall(answer))
    if not cited:
        return False, []
    fabricated = sorted(cited - retrieved_article_ids)
    return (not fabricated), fabricated
```

### 6.15 `src/app/streamlit_app.py`

```python
"""Streamlit frontend. Research-mode framing throughout."""
from __future__ import annotations

import streamlit as st

from src.config import load_config
from src.generation.llm_client import LLMClient
from src.generation.prompts import (
    REFUSAL_MESSAGE,
    SYSTEM_PROMPT,
    USER_TEMPLATE,
    format_sources,
)
from src.generation.verifier import verify_answer


st.set_page_config(
    page_title="delhi-legal-assist (research)",
    page_icon="⚖️",
    layout="wide",
)


@st.cache_resource
def get_pipeline():
    # The full pipeline (retriever + reranker + LLM) is wired here.
    # In v0.1 the agent should generate a TODO stub that returns a dummy
    # retriever and a real LLMClient, so the UI runs against an empty KB
    # and exercises the refusal path end-to-end.
    cfg = load_config()
    llm = LLMClient(cfg.llm_endpoint, cfg.llm_model, cfg.llm_temperature, cfg.llm_max_tokens)
    return cfg, llm, None  # retriever wired up in build_index.py runtime


st.title("delhi-legal-assist")
st.caption(
    "Research RAG over Indian legal primary sources. "
    "**Not legal advice.** See DISCLAIMER.md."
)

st.warning(
    "⚠️ This is a technical research project. No knowledge-base articles "
    "have been reviewed by a qualified lawyer. Output may be incomplete "
    "or incorrect. Verify against cited primary sources before relying "
    "on any information."
)

cfg, llm, retriever = get_pipeline()

query = st.text_area("Your question", height=120, placeholder=
    "e.g. What does the Transfer of Property Act say about notice to quit?")

if st.button("Search", type="primary") and query.strip():
    if retriever is None:
        st.info("Knowledge base is empty in this scaffold release. "
                "Refusal path:")
        st.markdown(REFUSAL_MESSAGE)
    else:
        with st.spinner("Retrieving sources..."):
            results, confident = retriever.retrieve(query, k=cfg.top_k)

        if not confident:
            st.warning("Low retrieval confidence.")
            st.markdown(REFUSAL_MESSAGE)
        else:
            user_prompt = USER_TEMPLATE.format(
                query=query, formatted_sources=format_sources(results)
            )
            with st.spinner("Generating..."):
                answer = llm.generate(SYSTEM_PROMPT, user_prompt)
            retrieved_ids = {r.article_id for r in results}
            ok, fabricated = verify_answer(answer, retrieved_ids)
            if not ok:
                st.error("Answer failed citation verification. Suppressed.")
                st.caption(f"Fabricated or missing citations: {fabricated}")
                st.markdown(REFUSAL_MESSAGE)
            else:
                st.markdown(answer)
                with st.expander("Retrieved sources"):
                    for r in results:
                        st.markdown(
                            f"**{r.article_title}** "
                            f"(`{r.article_id}`, rerank={r.rerank_score:.2f}, "
                            f"status={r.article_status})"
                        )
                        st.code(r.text[:600] + ("..." if len(r.text) > 600 else ""))

st.divider()
st.caption(
    "Sources: India Code, Delhi Government Legislative Department, "
    "Delhi High Court, NJDG. "
    "If you have a real legal problem, call DSLSA helpline 1516."
)
```

### 6.16 `scripts/download_models.py`

```python
"""Download the open-weights models used by the system into the local HF cache."""
from __future__ import annotations

from huggingface_hub import snapshot_download

MODELS = [
    "law-ai/InLegalBERT",
    "BAAI/bge-reranker-v2-m3",
]

# The generation model is large; pull it separately via vLLM at serve time
# or uncomment one of these to pre-fetch:
# "Qwen/Qwen3-8B-Instruct-AWQ",
# "meta-llama/Llama-3.3-8B-Instruct",


def main() -> None:
    for m in MODELS:
        print(f"Downloading {m}...")
        snapshot_download(repo_id=m)
    print("Done.")


if __name__ == "__main__":
    main()
```

### 6.17 `scripts/build_index.py`

```python
"""Build the BM25 and dense indexes from the knowledge base."""
from __future__ import annotations

import pickle
from pathlib import Path

from rank_bm25 import BM25Okapi

from src.config import load_config
from src.indexing.embeddings import Embedder
from src.indexing.vector_store import VectorStore
from src.ingestion.chunker import chunk_article
from src.ingestion.markdown_loader import load_kb


def main() -> None:
    cfg = load_config()
    articles = load_kb(cfg.kb_root)
    print(f"Loaded {len(articles)} non-empty KB articles.")

    if not articles:
        print("Knowledge base is empty. Nothing to index. "
              "Author articles under knowledge_base/statutes/ and rerun.")
        return

    chunks = [c for a in articles for c in chunk_article(a)]
    print(f"Chunked into {len(chunks)} pieces.")

    embedder = Embedder(cfg.embedding_model)
    vectors = embedder.encode([c.text for c in chunks])

    vs = VectorStore(cfg.qdrant_host, cfg.qdrant_port, cfg.qdrant_collection, embedder.dim)
    vs.upsert(chunks, vectors)

    bm25 = BM25Okapi([c.text.lower().split() for c in chunks])
    cfg.data_root.mkdir(parents=True, exist_ok=True)
    with open(cfg.data_root / "bm25.pkl", "wb") as f:
        pickle.dump({"bm25": bm25, "chunks": chunks}, f)

    print("Index built.")


if __name__ == "__main__":
    main()
```

### 6.18 `tests/test_markdown_loader.py`

```python
"""Tests that empty template files are skipped and valid frontmatter parses."""
from pathlib import Path
import tempfile

from src.ingestion.markdown_loader import load_kb


def test_empty_template_is_skipped():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "empty.md"
        p.write_text("---\nid: x\ntitle: x\nstatus: unreviewed-primary-sources-only\n"
                     "jurisdiction: [Delhi]\ntopic: tenancy\naudience: any\n"
                     "language: en\n---\n\n<!-- TODO -->")
        assert load_kb(Path(tmp)) == []
```

### 6.19 `tests/test_verifier.py`

```python
from src.generation.verifier import verify_answer


def test_valid_citation():
    ok, fab = verify_answer("The Act says X [dl-tenancy-deposit-recovery, S.27].",
                            {"dl-tenancy-deposit-recovery"})
    assert ok and fab == []


def test_fabricated_citation():
    ok, fab = verify_answer("The Act says X [fake-article-id, S.99].", set())
    assert not ok
    assert fab == ["fake-article-id"]


def test_no_citation_fails():
    ok, fab = verify_answer("The Act says X.", {"dl-tenancy-deposit-recovery"})
    assert not ok
```

### 6.20 `tests/test_refusal.py`

```python
"""Smoke test that the refusal message is well-formed."""
from src.generation.prompts import REFUSAL_MESSAGE


def test_refusal_mentions_dslsa():
    assert "1516" in REFUSAL_MESSAGE
    assert "Nyaaya" in REFUSAL_MESSAGE
```

---

## 7. `.gitignore`

```
__pycache__/
*.py[cod]
.venv/
venv/
.env
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/
dist/
build/
data/
!data/.gitkeep
.streamlit/secrets.toml
```

---

## 8. `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: ruff check src tests scripts
      - run: pytest -v
```

---

## 9. Instructions to the agent

1. Create the repository structure exactly as in Section 3.
2. Generate file contents as specified in Sections 4–8. Files marked `[full]`
   get the literal content shown. Files marked `[skeleton]` get the Python
   code shown. Files marked `[empty template]` get only the frontmatter
   shown with the `TODO` comment body.
3. Do NOT invent any legal content. Do NOT fill in the empty article
   templates with statutory text. Do NOT add features beyond what is in
   this specification.
4. Use the Apache License 2.0 standard text for `LICENSE` (the full
   official text, not a summary).
5. Use Contributor Covenant 2.1 standard text for `CODE_OF_CONDUCT.md`.
6. Initial commit message: `chore: initial scaffold from SPECIFICATION.md`.
7. Do not push to a remote; leave that to the human maintainer.
