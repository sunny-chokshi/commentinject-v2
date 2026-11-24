# CommentInject v2 as a RealVuln comment-robustness target set

[RealVuln](https://github.com/kolega-ai/Real-Vuln-Benchmark) (Kolega.Dev) is an open Python/JS/Java benchmark for SAST and LLM security scanners. It scores a scanner on each **target repo** against `ground-truth/{slug}/ground-truth.json`. In that file, real vulnerabilities have `is_vulnerable: true` and false-positive traps have `is_vulnerable: false`. Scanner output is Semgrep-compatible JSON in `scan-results/{slug}/{scanner}/results.json`, and its LLM runners write the same format. RealVuln has no comment-perturbation axis.

**Proposed contribution:** add CommentInject's matched pairs as a set of RealVuln targets (its CONTRIBUTING route 1, "add a new target repo with ground truth"). The pieces map directly:

| CommentInject | RealVuln |
|---|---|
| vulnerable twin | finding, `is_vulnerable: true` |
| minimally fixed twin | false-positive trap, `is_vulnerable: false` (1 trap per vuln; RealVuln asks for at least 1 per 5) |
| comment condition (clean, doc, 12 strategies) | separate target |
| robustness | change in RealVuln's own TPR / FPR / F3 between `clean` and each comment target |

The adapter (`results_to_predictions.py`) goes the other way. It turns any RealVuln-format results on these targets, including RealVuln's 13+ LLM scanners, into `case_id,flagged`. `scripts/score_predictions.py` then adds the d′/c split, the TOST equivalence test and pair-clustered CIs.

## Layout: 28 targets of 30 files

```
python3 -I integrations/realvuln/to_realvuln.py --out OUT [--repo-url URL --commit-sha SHA40]
OUT/targets/realvuln-commentinject-{condition}-{a|b}/V01.py ... V30.py
OUT/ground-truth/realvuln-commentinject-{condition}-{a|b}/ground-truth.json
OUT/case_map.csv
```

- **One file per case.** The name is just the pair id (`V07.py`), so no label word appears in any path. File content is the case `code` from `data/cases.jsonl` plus a newline, and the sha256 is checked.
- **Each target holds exactly one twin of every pair: 15 vulnerable and 15 fixed.** RealVuln's single-turn LLM runner puts a whole target into one prompt, and the agentic runner lets the model browse it. If both twins sat side by side, the task would become "spot the difference". The vulnerable/fixed split is a fixed salted-hash assignment and is identical in every condition, so `{cond}-a` differs from `clean-a` only in the comments.
- **Ground truth:** `type: 4` (benchmark roll-up), `language: python`, `severity: "unrated"`, and no CVSS block, so no CVSS is invented. `location` spans the function's `def` line to its last line. `acceptable_cwes` follows RealVuln's `config/cwe-families.json` (for example CWE-327 → {327, 328} and CWE-330 → {330, 338}). An extra `commentinject` object on each finding carries `case_id` and `sha256`. RealVuln's validator ignores extra fields.
- **Placeholders:** `repo_url` and `commit_sha` (40 zeros) pass the validator but must be replaced. RealVuln clones `repo_url` and checks out `commit_sha` (see `clone_repos.py`), and it hosts its targets as mirrors (for example `kolega-ai-dev/realvuln-pygoat`). One public repo can hold all 28 targets as 28 commits (orphan branches), each with a 30-file tree. Their cloner fetches each target by SHA without any tooling change.

## Tests

```bash
python3 -I integrations/realvuln/tests/test_realvuln.py                       # stdlib checks (RealVuln parts skip)
REALVULN_DIR=/path/to/Real-Vuln-Benchmark python3 -I integrations/realvuln/tests/test_realvuln.py
```

The tests check:
- the shape: 28 × 30, each of the 840 cases exactly once, bytes and sha256 match;
- one twin per pair, a 15/15 balance, the same split in every condition, and no label words in paths;
- ground truth matches `cases.jsonl`;
- **RealVuln's own `validate_gt.validate_gt` reports 0 errors** on all 28 files;
- **RealVuln's loader, Semgrep parser, matcher and scorecard** give TP/FP/FN/TN = 15/0/0/15 for an oracle, 15/15/0/0 for flag-everything and 0/0/15/15 for an empty result on every target;
- the adapter's `any`/`cwe` modes and the Bandit converter.

## SAST baseline: a comment-blind tool should show no shift

```bash
python3 -I integrations/realvuln/run_sast_baseline.py --tool bandit --bin $VENV/bin/bandit \
  --work $SCRATCH/realvuln_work_bandit --out results/sast_baselines/bandit --realvuln-dir $RV
```

The script builds the targets, runs the tool with `cwd` set to each target, and converts Bandit JSON to Semgrep format (`bandit_to_semgrep.py`). It then writes predictions in two modes:
- **`any`:** any finding in the file counts as a flag. This is CommentInject's binary task.
- **`cwe`:** a finding counts only if its CWE is acceptable and it falls within ±10 lines. This is RealVuln's matching.

It scores both modes with `scripts/score_predictions.py`, and scores RealVuln's own per-target scorecards (`realvuln_scores.csv`). The results are in `results/sast_baselines/bandit/` and `LOCAL_TEST_LOG.md`.

`run_sast_baseline.py --tool semgrep --semgrep-config RULES.yaml` is also wired up but was not run. It needs a Semgrep registry ruleset downloaded or pinned locally.

## Status and open items before any upstream proposal

- Local only. Nothing has been opened, posted or forked. The dataset is 2.0.0-rc2 and unpublished, and human review of the twins is still in progress.
- Needed before proposing upstream:
  - a public mirror and real `repo_url`/`commit_sha` values;
  - `authorship` stated by the dataset authors (currently `unknown`/`low`);
  - an `evidence.source` the RealVuln maintainers accept (currently `manual_review`, with the construction described in the evidence text).
- RealVuln's matcher counts **findings** as false positives: several findings on one fixed twin, or a wrong-CWE finding on a vulnerable twin, each count. Its FPR therefore differs from CommentInject's case-level FPR. Use the adapter for d′/c.
- RealVuln's CONTRIBUTING suggests opening an issue first. A natural next step: an issue proposing the 28 targets plus the adapter, with the Bandit baseline as a worked example. It has not been drafted or posted.
