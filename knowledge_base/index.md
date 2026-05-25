# Knowledge Base — Article Index

This file is the authoritative catalog of all articles in `knowledge_base/`.
It is updated whenever an article is added, modified, or deprecated.

> **Note**: All articles currently carry `status: unreviewed-primary-sources-only`.
> No article has been reviewed by a qualified legal reviewer.
> See [DISCLAIMER.md](../DISCLAIMER.md).

---

## Statutes

Articles paraphrasing specific statutory provisions, section by section.

| File | Title | Topic | Audience | Status |
|------|-------|-------|----------|--------|
| [statutes/dl-tenancy-section-106-notice.md](./statutes/dl-tenancy-section-106-notice.md) | Section 106 TPA notice requirements | tenancy | any | unreviewed-primary-sources-only |
| [statutes/dl-tenancy-deposit-recovery.md](./statutes/dl-tenancy-deposit-recovery.md) | Security deposit recovery under Delhi tenancy law | tenancy | tenant | unreviewed-primary-sources-only |
| [statutes/dl-tenancy-rent-agreement.md](./statutes/dl-tenancy-rent-agreement.md) | Rent agreement requirements under Delhi tenancy law | tenancy | any | unreviewed-primary-sources-only |
| [statutes/dl-rera-complaint-filing.md](./statutes/dl-rera-complaint-filing.md) | RERA complaint filing procedure (Delhi) | rera | buyer | unreviewed-primary-sources-only |
| [statutes/dl-property-mutation.md](./statutes/dl-property-mutation.md) | Property mutation procedure (Delhi) | property | buyer | unreviewed-primary-sources-only |

---

## Concepts

*(None yet — concept pages are thin pointer pages linking to statute articles.)*

---

## Entities

*(None yet — entity pages list constitutive Acts and statutory functions
for regulatory bodies such as Delhi RERA, DDA, MCD.)*

---

## Adding a new article

1. Create a file under `knowledge_base/statutes/`, `knowledge_base/concepts/`,
   or `knowledge_base/entities/` following the naming convention
   `<jurisdiction>-<topic>-<subtopic>.md`.
2. Add valid YAML frontmatter per [SCHEMA.md](./SCHEMA.md).
3. Add an entry to the table above in the correct section.
4. Open a PR per the ingest protocol in `AGENTS.md §4`.

## Deprecating an article

Set `status: deprecated` in the article frontmatter and update the table
above accordingly. Do not delete the file; deprecated articles remain for
citation-chain integrity.
