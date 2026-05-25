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
