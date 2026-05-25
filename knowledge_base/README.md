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
