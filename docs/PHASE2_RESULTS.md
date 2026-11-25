# Phase 2 results (corrected data, 2.0.0-rc2/rc3)

Exploratory until the blinded human twin review is complete.

**Seeds and determinism.** All results come from one deterministic run. A repeat with seed 1 (3,360 trials) gave identical output, confirming determinism rather than independently replicating the results: 3,360/3,360 identical responses, so every table below is identical for both seeds. A partial seed-2 run (587 trials) was also 587/587 identical and was stopped. With Ollama 0.40.6 at temperature 0 the sampling seed has no effect on these models, so seed-to-seed variation is zero; decoding-temperature robustness is not tested and is listed as a limitation. Source: `results/phase2/raw_seed0_rc2.jsonl`
(3,360 trials = 4 models × 840; the 56 V10 fixed-twin trials were re-run after the rc2 fix with identical model digests, seed, prompt and settings).
Full tables: `results/phase2/analysis_seed0_rc2/ANALYSIS_v2.md`. The rc1 run is kept unchanged (`raw_seed0.jsonl`, `analysis_seed0_rc1/`).

| Model (digest) | Clean bAcc | Clean FPR | Δd′ pooled [95% CI] | d′ 90% CI (TOST ±0.5) | Δc [95% CI] | Reading |
|---|---|---|---|---|---|---|
| qwen3.5:4b, think off (d8b0f5e9760c) | 0.817 | 0.367 | −0.63 [−1.12, −0.03] | [−1.02, −0.12], not equivalent | +0.63 [+0.18, +1.11] | **discrimination loss** (same direction as the Phase 1 pilot; not an independent replication) |
| deepseek-coder:6.7b (ce298d984115) | 0.550 | 0.833 | −0.53 [−1.30, +0.05] | [−1.18, −0.03], not equivalent | +0.62 [+0.34, +1.06] | criterion shift, d′ undetermined (same direction as the pilot) |
| qwen2.5-coder:7b (dae161e27b0e) | 0.617 | 0.733 | +0.34 [−0.25, +0.91] | [−0.18, +0.80], not equivalent | +0.29 [−0.02, +0.64] | inconclusive; ΔbAcc +0.078 [+0.004, +0.161] (comments lowered FPR more than TPR, as in the pilot) |
| llama3.1:8b (46e0c10c039e) | 0.500 | 1.000 | — | — | — | ceiling: flags everything; not interpretable |

Δ = pooled adversarial (12 strategies) minus clean; two-way (pair × strategy) bootstrap; Ollama 0.40.6, temperature 0, seed 0.

**What the V10 fix changed:** the fixed twin is now flagged less often by qwen2.5 (14/14 → 7/14) and qwen3.5 (10/14 → 8/14), and slightly more by deepseek (8/14 → 10/14). No pooled reading changed.
**Benign comments (`doc`):** no detectable cost for qwen2.5 (d′ equivalent at ±0.25); inconclusive for qwen3.5 and deepseek.
**Paid probe (separate, 5 pairs):** no verdict changed for Gemini 3.8 Flash, Haiku 5.5 or Sonnet 5.5 (`docs/API_PROBE_RESULTS_2026-11-24.md`).
