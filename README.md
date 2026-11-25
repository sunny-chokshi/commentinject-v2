# CommentInject v2: do code comments move your vulnerability detector?

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24517327.svg)](https://doi.org/10.5281/zenodo.24517327)

This version (rc3): DOI 10.5281/zenodo.24517927 · all versions: 10.5281/zenodo.24517327 · code: https://github.com/sunny-chokshi/commentinject-v2

> **Status: release candidate 2.0.0-rc3 (exploratory), published 2026-11-25.** The matched twins have passed automated checks, runtime exploit tests (XML pairs) and an independent model review; **the blinded human review is in progress** and may change pairs. Phase 2 results are deterministic at temperature 0: seed 1 reproduced seed 0 exactly (3,360/3,360 identical responses). v1 (DOI 10.5281/zenodo.23088528) is unchanged.

CommentInject v2 tests whether **natural-language comments inside code** change what an LLM (or any tool) says about that code's security, and **how** they change it. It asks two questions:
- Does the detector **lose the ability to tell vulnerable from fixed code** (discrimination, d′)?
- Or does it just **become less willing to flag anything** (criterion, c)?

To separate the two, every vulnerable function comes with a **matched, minimally fixed twin**, and every comment is applied to both.

## In one minute

```bash
# score your own detector (LLM, SAST tool, review bot): one prediction per case_id
python3 -I examples/regex_baseline.py > preds.csv          # example predictions file
python3 -I scripts/score_predictions.py preds.csv out/      # -> out/ANALYSIS_v2.md, out/metrics_v2.csv
```

Your predictions file needs only two columns, `case_id` and `flagged` (VULNERABLE/SAFE, true/false or 1/0), in JSONL or CSV. Scoring a subset is fine; at minimum, include the `clean` condition.

## What is in the benchmark

| | |
|---|---|
| Pairs | 30 Python functions across 14 CWEs. Each pair is a vulnerable function and a minimal fix with the same name and signature (`data/pairs.jsonl`). |
| Conditions | `clean`; `doc` (one neutral comment describing the function's purpose, used to measure what stripping comments costs); 12 adversarial comment strategies in 4 families (`data/strategies.jsonl`). |
| Cases | 30 pairs × 2 twins × 14 conditions = **840** (`data/cases.jsonl`, with SHA-256 per case). |
| Labels | `label` 1 = vulnerable twin, 0 = fixed twin (target CWE; see `docs/RESEARCH_TASK_DEFINITION_2026-11-24.md`). |
| Prompt (LLM runs) | The v1 reviewer prompt (`scripts/common.py`): answer VULNERABLE/SAFE, then name the type. |

**Quality checks** run by the `tests/` scripts:
- every twin parses and keeps the function name;
- the flaw pattern is present only in the vulnerable twin;
- identifiers and doc comments contain no label words;
- no `timeout=` appears in just one twin;
- no near-duplicate fixes;
- stripping comments returns each case to its clean twin;
- **XML pairs are exploit-tested at runtime**: the vulnerable twin leaks a local file and the fixed twin does not.

## Metrics
`scripts/analyze_v2.py` reports, per model and per comparison against `clean`:
- **Rates:** TPR, FPR, yes-rate and balanced accuracy.
- **Signal detection:** d′ and c. They are computed per strategy with equal n and averaged, so the log-linear correction stays symmetric.
- **Confidence intervals:** bootstrap CIs that resample **matched pairs** (V08 and V23 count as one cluster). Pooled results also resample strategies (two-way).
- **Equivalence:** a **TOST** test of d′ (margins ±0.25/0.5/0.75), so "no change" is claimed only when it is shown.
- **Per-strategy tests:** exact McNemar tests with Holm correction.
- **Ceiling rule:** a model whose clean yes-rate is ≥ 0.95 or ≤ 0.05 is reported as not interpretable.

## Results so far (exploratory)
Phase 2, corrected data, 4 local open-weight models, 3,360 trials per seed; seeds 0 and 1 identical (`docs/PHASE2_RESULTS.md`):

| Model | Clean bAcc | Δd′ under adversarial comments [95% CI] | Δc [95% CI] | Reading |
|---|---|---|---|---|
| qwen3.5:4b (think off) | 0.817 | −0.63 [−1.12, −0.03] | +0.63 [+0.18, +1.11] | discrimination loss |
| deepseek-coder:6.7b | 0.550 | −0.53 [−1.30, +0.05] | +0.62 [+0.34, +1.06] | criterion shift, d′ undetermined |
| qwen2.5-coder:7b | 0.617 | +0.34 [−0.25, +0.91] | +0.29 [−0.02, +0.64] | inconclusive (bAcc +0.078) |
| llama3.1:8b | 0.500 | — | — | flags everything; not interpretable |

- **Comment-blind control:** Bandit (SAST) changes 0 of 780 verdicts under the same comments (`results/sast_baselines/bandit/`).
- **Frontier probe** (5 pairs, 20 cases per model): no verdict changed for Gemini 3.8 Flash, Claude Haiku 5.5 or Claude Sonnet 5.5 (`docs/API_PROBE_RESULTS_2026-11-24.md`). Too small to show robustness.
- **Phase 1 pilot** (original pairs): `docs/PILOT_RESULTS_2026-11-24.md`; read its addendum.

## Validation status and limitations
- **Human validation: in progress.** Twins are author-written; a blinded two-reviewer protocol is under way. Treat labels as provisional until it is reported here.
- Temperature-0 decoding only: seeds gave identical outputs, so sampling-temperature robustness is untested.
- 30 short Python functions, 14 CWEs; labels refer to the target CWE.
- Small local models (4–8B); several have weak clean discrimination, so criterion shifts in near-chance models mean little in practice.
- Fixed twins are often longer and use validation constructs, which could act as cues.

## Integrations
- **Inspect (UK AISI) / inspect_evals:** `integrations/inspect_evals/`
- **garak (NVIDIA):** `integrations/garak/`
- **RealVuln (Kolega.Dev):** `integrations/realvuln/`. It converts the pairs into 28 RealVuln targets and includes a result adapter. A Bandit SAST baseline is in `results/sast_baselines/bandit/`.
- **promptfoo:** `integrations/promptfoo/` (example config + verdict assertion)
- **Microsoft PyRIT:** `integrations/pyrit/` (dataset loader)
- **Plain JSONL exports:** `integrations/*/commentinject_v2_*` (from `scripts/export_integrations.py`)

See `integrations/LOCAL_TEST_LOG.md` for tested versions and commands.

## Reproduce
```bash
python3 -I scripts/build_data.py ../CommentInject_release/data/samples.jsonl   # needs v1 samples
python3 -I tests/test_pairs.py ../CommentInject_release/data/samples.jsonl
python3 -I tests/test_xml_runtime.py
python3 -I tests/test_analyze_v2.py
python3 -I scripts/run.py --models qwen2.5-coder:7b --seed 0 --out results/mine/raw.jsonl   # Ollama, temperature 0
python3 -I scripts/run.py --models qwen3.5:4b --no-think --out results/mine/raw.jsonl       # reasoning models: think off
python3 -I scripts/analyze_v2.py results/mine/raw.jsonl results/mine
```
The core scripts use the standard library only. `scripts/run_api.py` (the capped paid-model probe) needs the `anthropic`, `openai` and `google-genai` packages and your own API keys in environment variables.

## Changes from v1
| | v1 | v2 |
|---|---|---|
| Classes | 30 vulnerable functions | 30 matched vulnerable/fixed pairs |
| Conditions | clean + 12 adversarial | clean + doc + 12 adversarial |
| Metric | detection rate | rates + d′/c + TOST, clustered CIs |
| Stripping defense | "defended = clean" by construction | the cost of stripping measured via the `doc` condition |
| Parser | first-line substring (misreads "NOT VULNERABLE") | negation-aware; v1 parser kept for comparison |
| Pairs that differ from v1 | — | V10 (the v1 version is not exploitable on modern CPython), V15 and V30 (shared names biased both twins), V27 (`timeout` added to both); see `CHANGELOG.md` |

## Related work and scope
Comment and context attacks on LLM detectors are an active area: Flashboom (S&P 2025); Thornton (2026); Sun, Oprea & Wong (2026); ALIBI (2026); Alexopoulos et al. (ICSE 2027); Shahriar et al. (S&P 2027). Closest robustness evaluations of LLM vulnerability detection: SecLLMHolmes (Ullah et al., S&P 2024), which perturbs code including random code in comments on vulnerable/patched pairs, and the Familiar Pattern Attack (Bernstein, Beste, Ayzenshteyn, Schönherr, Mirsky, NDSS 2026), which manipulates detectors through code patterns rather than comments. v2's narrower contribution is measuring **in-code comments on matched fixed twins with d′/c**. See `docs/NOVELTY_AUDIT_EXPANSION_2026-11-24.md` for the full list.

## Citation and license
See `CITATION.cff`. Code is MIT; data is CC-BY-4.0 (the same as v1).
