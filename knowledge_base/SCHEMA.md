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
