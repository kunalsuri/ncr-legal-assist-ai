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
