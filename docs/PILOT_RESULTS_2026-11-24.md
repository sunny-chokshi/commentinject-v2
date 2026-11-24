# CommentInject v2 local pilot: results and honest reading (2026-11-24)

The full tables are in `results/pilot/ANALYSIS.md` and `results/pilot/metrics.csv`, built from `results/pilot/raw.jsonl` (3,360 trials).

- **Design:** 30 matched pairs (vulnerable v1 function and a safe twin) under 14 conditions: clean, doc (a neutral comment), and 12 adversarial strategies. Each case was run once.
- **Models:** 4 local models through Ollama, temperature 0, seed 0, with the model digests recorded.
- **Prompt:** identical to v1 Study 1.
- **Parsing:** no reply was unparsed, and the v1 and v2 parsers agreed on every trial.
- **Pre-registered rules:** the hypotheses and the reading rule (`scripts/analyze.py` docstring; `docs/NOVELTY_AUDIT_2026-11-24.md`) were fixed before any results were read.

## Protocol deviation (qwen3.5:4b)
qwen3.5:4b is a reasoning model. With hidden reasoning on, each trial took 17–144 seconds, so the 840 trials would have taken about 12 hours.

- After 19 trials the run was stopped and repeated with Ollama `think: false`. Those rows are labelled `qwen3.5:4b+nothink`.
- The 19 reasoning-mode rows are kept unchanged in `results/pilot/qwen35_4b_THINKING_partial_19rows.jsonl` and are not analysed.
- The results below therefore describe qwen3.5:4b **without reasoning**. Reasoning mode is untested.

## Pooled results (adversarial, all 12 strategies, vs clean)

| Model | Clean TPR / FPR (bAcc, d′) | Adversarial TPR / FPR (bAcc) | ΔTPR | ΔFPR | d′ shift [95% CI] | c shift [95% CI] | Reading (pre-registered rule) |
|---|---|---|---|---|---|---|---|
| deepseek-coder:6.7b | 0.933 / 0.867 (0.53, 0.34) | 0.703 / 0.739 (0.48) | −0.231 | −0.128 | −0.49 [−2.05, 0.26] | +0.71 [0.46, 1.51] | operating-point shift |
| qwen2.5-coder:7b | 0.967 / 0.733 (0.62, 1.06) | 0.931 / 0.558 (0.69) | −0.036 | −0.175 | +0.13 [−1.19, 0.64] | +0.41 [0.19, 1.07] | operating-point shift |
| qwen3.5:4b (think off) | 1.000 / 0.333 (0.83, 2.56) | 0.814 / 0.289 (0.76) | −0.186 | −0.044 | −1.98 [−2.40, −1.57] | +1.11 [0.95, 1.28] | **discrimination loss** |
| llama3.1:8b | 1.000 / 1.000 (0.50, 0.00) | 0.994 / 1.000 (0.50) | −0.006 | 0.000 | −0.53 [−0.90, 0.00] | +0.27 [0.00, 0.45] | no clear effect (ceiling: flags everything) |

The doc condition (benign purpose comments, which is what stripping removes) had **no clear effect on any model**. The largest change was qwen3.5: d′ −0.83 [−1.41, 0.00], a CI that only just touches 0.

Per-strategy exact McNemar tests (Holm-corrected across the 12 strategies, p < .05):

| Model | Vulnerable twins flipped | Safe twins flipped |
|---|---|---|
| deepseek | 3 (authorial_confidence, authority_claim, misleading_context) | 2 (authorial_confidence, authority_claim) |
| qwen2.5 | 0 | 3 (formal_verification, misleading_context, scope_limitation) |
| qwen3.5 | 2 (false_reassurance, scope_limitation) | 2 (false_reassurance, scope_limitation) |
| llama | 0 | 0 |

## Hypotheses

- **H1 (adversarial comments also lower FPR on safe twins): supported in 3 of 4 models.** The pooled FPR fell for deepseek, qwen2.5 and qwen3.5, with Holm-significant safe-twin flips for 2–3 strategies each. llama was uninformative because it flags 100% of everything.
  - Not uniform: for qwen3.5, two strategies *raised* FPR (authorial_confidence +0.27, Holm p = .008; distraction_comment +0.27).
- **H2 (an operating-point shift in at least one model): supported, formally, for deepseek and qwen2.5.** Important caveat: both models barely discriminate even on clean code (clean bAcc 0.53 and 0.62; deepseek d′ 0.34). A "criterion shift" in a model that is near chance means little in practice.
  - **The only model that discriminates well, qwen3.5 (clean bAcc 0.83), shows a real discrimination loss**, not just a threshold shift.
  - This partly **contradicts** the threshold-shift-only framing in Sunny's ICAISG HF1052, which must not be cited as confirmed by v2.
- **H3 (benign comments change detection, so stripping has a cost): not supported.** No model showed a clear doc-condition effect. The pilot does not show a stripping cost.

## What the pilot does show (and what it does not)

1. **Detection rate alone gives the wrong picture.**
   - qwen2.5: in v1's TPR-only terms the attack cost 3.6 points. With safe twins the main change is a 17.5-point *drop in false alarms*, and balanced accuracy *rose* (0.62 → 0.69).
   - deepseek: TPR fell 23 points, but FPR also fell 13 points.
   - Matched safe controls change the reading of the result. This is the methodological point v2 was built to test, and it holds in this pilot.
2. **The effect type differs by model:** a criterion shift in weak models and a discrimination loss in the strongest one tested. This fits the "reconcile conflicting findings" question in the novelty audit, but 4 small models cannot answer it.
3. **Not shown:**
   - anything about frontier or commercial models;
   - reasoning-mode behaviour;
   - run-to-run variance (one run each);
   - generality beyond 30 Python functions;
   - whether the safe twins are fully safe (no external review yet, task T23).
4. **The small models' baseline is poor:**
   - three of the four flag 73–100% of safe code;
   - the reading is limited to weak detectors.

## Next steps (none taken; each needs Sunny)
- **External review of the 30 safe twins (T23)** before any scale-up or write-up.
- **Paid-model token probe (< $1)**, then the pilot grid (≈ $15–25, cap $50), only with an approved budget and keys entered by Sunny. Frontier models are where the Thornton (null) vs v1/ALIBI (effect) disagreement lies.
- **Stronger local models or more seeds** (free): a qwen3.5 reasoning-mode subset overnight (≈ 12 h for 840; a 1-pair-per-strategy subset would take ≈ 1 h), and repeat runs with different seeds.
- **No claim of significance or novelty beyond `NOVELTY_AUDIT` section 3.** This is a pilot.

---
## Addendum (2026-11-24, after the second external audit): corrected analysis

The tables above come from `scripts/analyze.py` and are kept unchanged as the record. The corrected analysis is `scripts/analyze_v2.py`, with output in `results/pilot_analysis_v2/ANALYSIS_v2.md`. It changes three things:
- "operating-point shift" now needs **TOST equivalence** of d′ (primary margin ±0.5), not merely a CI that includes 0;
- V08 and V23 are bootstrapped as one cluster, and pooled CIs resample both pairs and strategies;
- pooled d′ and c are averaged per strategy, so the log-linear correction uses the same n as the clean baseline. The original analysis compared n = 360 against a clean baseline replicated 12 times, which inflated d′ shifts when a rate was at 0 or 1.

Restated pooled results (adversarial vs clean, two-way bootstrap):

| Model | Δd′ [95% CI] | Δc [95% CI] | ΔbAcc [95% CI] | Corrected reading | Original reading |
|---|---|---|---|---|---|
| deepseek-coder:6.7b | −0.44 [−1.22, +0.24] | +0.64 [+0.37, +1.08] | −0.051 [−0.126, +0.027] | criterion shift, **d′ undetermined** | operating-point shift |
| qwen2.5-coder:7b | +0.30 [−0.26, +0.79] | +0.30 [+0.01, +0.66] | **+0.069 [+0.009, +0.147]** | criterion shift, **d′ undetermined** | operating-point shift |
| qwen3.5:4b (think off) | **−0.75 [−1.26, −0.19]** | +0.64 [+0.19, +1.14] | −0.071 [−0.157, +0.011] | discrimination loss on d′. The bAcc CI includes 0, and clean TPR = 30/30 (ceiling) makes d′ depend on the correction. | discrimination loss (Δd′ −1.98, inflated) |
| llama3.1:8b | — | — | −0.003 | **ceiling: not interpretable** (clean yes-rate 1.00) | no clear effect |

Corrected hypothesis status:
- **H1, supported descriptively** in 3/4 models: FPR falls (Holm-significant safe-twin flips for 2–3 strategies per model).
- **H2, not established.** No model meets "criterion shift with d′ equivalent". In deepseek and qwen2.5 the threshold moved, but the data cannot say whether discrimination also changed. 30 pairs per class cannot reach a ±0.5 equivalence margin for these models. **The absence of a significant d′ change is not evidence that d′ was unchanged.**
- **H3, not demonstrated.**
  - qwen2.5: a stripping cost larger than ±0.5 d′ is ruled out (TOST).
  - deepseek and qwen3.5: inconclusive. For qwen3.5 the 90% CI is [−1.27, −0.08], so a cost cannot be excluded.
- **qwen2.5's rise in balanced accuracy under attack** (+0.069, CI excludes 0 under both bootstraps) is the most robust single descriptive result.

All corrected readings are exploratory: the margins and rule were set after the data were seen. They must be pre-registered for Phase 2.
