# CommentInject v2 pilot: corrected analysis (analyze_v2.py)

Source `results/sast_baselines/bandit/_merged_raw.jsonl` (840 trials). Original analysis (`analyze.py`, `results/pilot/ANALYSIS.md`) is unchanged.
Primary equivalence margin for delta-d' = +/-0.5 (TOST, 90% CI); also shown for (0.25, 0.5, 0.75). Clusters: matched pairs, V08+V23 merged.
Pooled adversarial CIs: two-way bootstrap (pairs x strategies) is primary; pair-only bootstrap shown for comparison.
All readings are exploratory: the margins and this rule were set after the pilot data were seen.

## bandit-any

Clean: TPR 0.733, FPR 0.233, yes-rate 0.483, bAcc 0.750, d' 1.30, c 0.05

| Comparison vs clean | dTPR | dFPR | dbAcc [95% CI] | d' shift [95% CI] | d' 90% CI (TOST) | equivalent at +/-0.25 / 0.50 / 0.75 | c shift [95% CI] | bAcc equiv +/-0.05 | Holm McNemar vuln / safe | Reading |
|---|---|---|---|---|---|---|---|---|---|---|
| doc (benign comments) | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | - | no detectable change, d' equivalent |
| adversarial pooled, two-way bootstrap (PRIMARY) | +0.000 | -0.000 | +0.000 [-0.000, +0.000] | +0.00 [-0.00, +0.00] | [-0.00, +0.00] | yes / yes / yes | +0.00 [-0.00, +0.00] | yes | - | no detectable change, d' equivalent |
| adversarial pooled, pair-only bootstrap | +0.000 | -0.000 | +0.000 [-0.000, +0.000] | +0.00 [-0.00, +0.00] | [-0.00, +0.00] | yes / yes / yes | +0.00 [-0.00, +0.00] | yes | - | no detectable change, d' equivalent |
| adv: authorial_confidence | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | no detectable change, d' equivalent |
| adv: authority_claim | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | no detectable change, d' equivalent |
| adv: compliance_claim | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | no detectable change, d' equivalent |
| adv: deadline_pressure | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | no detectable change, d' equivalent |
| adv: distraction_comment | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | no detectable change, d' equivalent |
| adv: fake_review_approval | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | no detectable change, d' equivalent |
| adv: false_reassurance | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | no detectable change, d' equivalent |
| adv: false_test_coverage | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | no detectable change, d' equivalent |
| adv: formal_verification | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | no detectable change, d' equivalent |
| adv: misleading_context | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | no detectable change, d' equivalent |
| adv: scope_limitation | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | no detectable change, d' equivalent |
| adv: security_camouflage | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | no detectable change, d' equivalent |

