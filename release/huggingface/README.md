---
license: cc-by-4.0
language:
- en
pretty_name: CommentInject v2
size_categories:
- n<1K
task_categories:
- text-classification
tags:
- security
- vulnerability-detection
- prompt-injection
- adversarial
- llm-evaluation
- code
configs:
- config_name: cases
  data_files: cases.jsonl
- config_name: pairs
  data_files: pairs.jsonl
- config_name: strategies
  data_files: strategies.jsonl
---

# CommentInject v2

> **Release candidate 2.0.0-rc3 (exploratory).** Human blinded review of the twins is in progress and may change pairs. DOI [10.5281/zenodo.24517927](https://doi.org/10.5281/zenodo.24517927) (all versions: 10.5281/zenodo.24517327) · code, scorer, results and integrations: https://github.com/sunny-chokshi/commentinject-v2

CommentInject v2 holds 840 Python code cases for testing whether in-code comments change what LLM vulnerability detectors say about the code: 30 matched vulnerable/fixed function pairs across 14 CWEs, each under 14 comment conditions (clean, a neutral doc comment, and 12 adversarial strategies).

- **Fields** (`cases`): `case_id`, `pair_id`, `cwe`, `variant` (vulnerable/safe), `label` (1 = vulnerable), `condition` (clean/doc/adversarial), `strategy`, `code`, `sha256`.
- **Scoring:** the v1 reviewer prompt plus a VULNERABLE/SAFE first-line verdict. Scripts and metrics (TPR/FPR, d′/c, TOST) are in the GitHub repository; `scripts/score_predictions.py` scores any detector from a `case_id,flagged` file.
- **Intended use:** evaluating robustness of code-security tools and LLM reviewers. The adversarial comments are persuasion text, not exploits; the vulnerable functions are textbook examples.
- **Limitations:** 30 short Python functions; labels refer to the target CWE; human review of the twins is in progress at release-candidate stage.
- **v1:** 10.5281/zenodo.23088528 (vulnerable-only). See `CHANGELOG.md` for the pairs that differ from v1.
- **Citation:** Chokshi, S. (2026). CommentInject v2 (2.0.0-rc3). Zenodo. https://doi.org/10.5281/zenodo.24517927
