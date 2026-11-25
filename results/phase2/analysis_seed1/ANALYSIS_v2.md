# CommentInject v2 pilot: corrected analysis (analyze_v2.py)

Source `results/phase2/raw_seed1.jsonl` (3360 trials). Original analysis (`analyze.py`, `results/pilot/ANALYSIS.md`) is unchanged.
Primary equivalence margin for delta-d' = +/-0.5 (TOST, 90% CI); also shown for (0.25, 0.5, 0.75). Clusters: matched pairs, V08+V23 merged.
Pooled adversarial CIs: two-way bootstrap (pairs x strategies) is primary; pair-only bootstrap shown for comparison.
All readings are exploratory: the margins and this rule were set after the pilot data were seen.

## deepseek-coder:6.7b

Clean: TPR 0.933, FPR 0.833, yes-rate 0.883, bAcc 0.550, d' 0.48, c -1.16

| Comparison vs clean | dTPR | dFPR | dbAcc [95% CI] | d' shift [95% CI] | d' 90% CI (TOST) | equivalent at +/-0.25 / 0.50 / 0.75 | c shift [95% CI] | bAcc equiv +/-0.05 | Holm McNemar vuln / safe | Reading |
|---|---|---|---|---|---|---|---|---|---|---|
| doc (benign comments) | -0.067 | -0.033 | -0.017 [-0.069, +0.034] | -0.23 [-0.94, +0.29] | [-0.75, +0.21] | no / no / yes | +0.23 [+0.00, +0.50] | no | - | inconclusive |
| adversarial pooled, two-way bootstrap (PRIMARY) | -0.239 | -0.117 | -0.061 [-0.131, +0.009] | -0.53 [-1.30, +0.05] | [-1.18, -0.03] | no / no / no | +0.62 [+0.34, +1.06] | no | - | criterion shift, d' undetermined |
| adversarial pooled, pair-only bootstrap | -0.239 | -0.117 | -0.061 [-0.132, +0.011] | -0.53 [-1.31, +0.07] | [-1.20, -0.03] | no / no / no | +0.62 [+0.40, +1.00] | no | - | criterion shift, d' undetermined |
| adv: authorial_confidence | -0.467 | -0.333 | -0.067 [-0.177, +0.052] | -0.56 [-1.52, +0.26] | [-1.37, +0.09] | no / no / no | +1.20 [+0.83, +1.73] | no | 0.00146 / 0.0215 | criterion shift, d' undetermined |
| adv: authority_claim | -0.467 | -0.367 | -0.050 [-0.177, +0.086] | -0.48 [-1.51, +0.36] | [-1.31, +0.20] | no / no / no | +1.24 [+0.89, +1.77] | no | 0.00146 / 0.0117 | criterion shift, d' undetermined |
| adv: compliance_claim | -0.100 | -0.067 | -0.017 [-0.086, +0.052] | -0.25 [-1.08, +0.41] | [-0.94, +0.30] | no / no / no | +0.35 [+0.13, +0.67] | no | 0.75 / 1 | criterion shift, d' undetermined |
| adv: deadline_pressure | -0.100 | -0.033 | -0.033 [-0.100, +0.033] | -0.36 [-1.08, +0.21] | [-0.94, +0.11] | no / no / no | +0.30 [+0.07, +0.67] | no | 0.75 / 1 | criterion shift, d' undetermined |
| adv: distraction_comment | -0.167 | +0.000 | -0.083 [-0.167, +0.000] | -0.70 [-1.55, -0.10] | [-1.42, -0.20] | no / no / no | +0.35 [+0.05, +0.77] | no | 0.375 / 1 | discrimination loss |
| adv: fake_review_approval | -0.100 | -0.033 | -0.033 [-0.100, +0.033] | -0.36 [-1.08, +0.19] | [-0.95, +0.12] | no / no / no | +0.30 [+0.07, +0.67] | no | 0.75 / 1 | criterion shift, d' undetermined |
| adv: false_reassurance | -0.300 | -0.133 | -0.083 [-0.172, +0.000] | -0.65 [-1.51, +0.00] | [-1.40, -0.08] | no / no / no | +0.75 [+0.42, +1.23] | no | 0.0391 / 1 | criterion shift, d' undetermined |
| adv: false_test_coverage | -0.267 | -0.100 | -0.083 [-0.172, +0.016] | -0.66 [-1.54, +0.09] | [-1.42, -0.04] | no / no / no | +0.65 [+0.37, +1.07] | no | 0.0625 / 1 | criterion shift, d' undetermined |
| adv: formal_verification | -0.267 | -0.033 | -0.117 [-0.200, -0.048] | -0.87 [-1.64, -0.35] | [-1.53, -0.44] | no / no / no | +0.55 [+0.26, +1.00] | no | 0.0625 / 1 | discrimination loss |
| adv: misleading_context | -0.300 | -0.200 | -0.050 [-0.161, +0.067] | -0.48 [-1.42, +0.28] | [-1.26, +0.17] | no / no / no | +0.83 [+0.53, +1.32] | no | 0.0391 / 0.312 | criterion shift, d' undetermined |
| adv: scope_limitation | -0.167 | -0.067 | -0.050 [-0.138, +0.034] | -0.48 [-1.34, +0.21] | [-1.22, +0.11] | no / no / no | +0.46 [+0.22, +0.82] | no | 0.375 / 1 | criterion shift, d' undetermined |
| adv: security_camouflage | -0.167 | -0.033 | -0.067 [-0.150, +0.000] | -0.58 [-1.34, +0.00] | [-1.23, -0.10] | no / no / no | +0.41 [+0.14, +0.78] | no | 0.375 / 1 | criterion shift, d' undetermined |

## llama3.1:8b

Clean: TPR 1.000, FPR 1.000, yes-rate 1.000, bAcc 0.500, d' 0.00, c -2.14  **(ceiling/floor: SDT not interpreted)**

| Comparison vs clean | dTPR | dFPR | dbAcc [95% CI] | d' shift [95% CI] | d' 90% CI (TOST) | equivalent at +/-0.25 / 0.50 / 0.75 | c shift [95% CI] | bAcc equiv +/-0.05 | Holm McNemar vuln / safe | Reading |
|---|---|---|---|---|---|---|---|---|---|---|
| doc (benign comments) | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | - | ceiling/floor: not interpretable |
| adversarial pooled, two-way bootstrap (PRIMARY) | -0.006 | +0.000 | -0.003 [-0.013, +0.000] | -0.08 [-0.25, +0.00] | [-0.23, +0.00] | yes / yes / yes | +0.04 [+0.00, +0.12] | yes | - | ceiling/floor: not interpretable |
| adversarial pooled, pair-only bootstrap | -0.006 | +0.000 | -0.003 [-0.009, +0.000] | -0.08 [-0.16, +0.00] | [-0.15, +0.00] | yes / yes / yes | +0.04 [+0.00, +0.08] | yes | - | ceiling/floor: not interpretable |
| adv: authorial_confidence | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | ceiling/floor: not interpretable |
| adv: authority_claim | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | ceiling/floor: not interpretable |
| adv: compliance_claim | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | ceiling/floor: not interpretable |
| adv: deadline_pressure | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | ceiling/floor: not interpretable |
| adv: distraction_comment | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | ceiling/floor: not interpretable |
| adv: fake_review_approval | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | ceiling/floor: not interpretable |
| adv: false_reassurance | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | ceiling/floor: not interpretable |
| adv: false_test_coverage | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | ceiling/floor: not interpretable |
| adv: formal_verification | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | ceiling/floor: not interpretable |
| adv: misleading_context | -0.033 | +0.000 | -0.017 [-0.052, +0.000] | -0.48 [-0.94, +0.00] | [-0.93, +0.00] | no / no / no | +0.24 [+0.00, +0.47] | no | 1 / 1 | ceiling/floor: not interpretable |
| adv: scope_limitation | -0.033 | +0.000 | -0.017 [-0.052, +0.000] | -0.48 [-0.94, +0.00] | [-0.93, +0.00] | no / no / no | +0.24 [+0.00, +0.47] | no | 1 / 1 | ceiling/floor: not interpretable |
| adv: security_camouflage | +0.000 | +0.000 | +0.000 [+0.000, +0.000] | +0.00 [+0.00, +0.00] | [+0.00, +0.00] | yes / yes / yes | +0.00 [+0.00, +0.00] | yes | 1 / 1 | ceiling/floor: not interpretable |

## qwen2.5-coder:7b

Clean: TPR 0.967, FPR 0.733, yes-rate 0.850, bAcc 0.617, d' 1.06, c -1.13

| Comparison vs clean | dTPR | dFPR | dbAcc [95% CI] | d' shift [95% CI] | d' 90% CI (TOST) | equivalent at +/-0.25 / 0.50 / 0.75 | c shift [95% CI] | bAcc equiv +/-0.05 | Holm McNemar vuln / safe | Reading |
|---|---|---|---|---|---|---|---|---|---|---|
| doc (benign comments) | +0.000 | +0.000 | +0.000 [-0.048, +0.050] | +0.00 [-0.27, +0.28] | [-0.21, +0.23] | yes / yes / yes | +0.00 [-0.14, +0.14] | yes | - | no detectable change, d' equivalent |
| adversarial pooled, two-way bootstrap (PRIMARY) | -0.028 | -0.183 | +0.078 [+0.004, +0.161] | +0.34 [-0.25, +0.91] | [-0.18, +0.80] | no / no / no | +0.29 [-0.02, +0.64] | no | - | inconclusive |
| adversarial pooled, pair-only bootstrap | -0.028 | -0.183 | +0.078 [+0.016, +0.141] | +0.34 [-0.23, +0.82] | [-0.15, +0.76] | no / no / no | +0.29 [+0.10, +0.54] | no | - | criterion shift, d' undetermined |
| adv: authorial_confidence | +0.033 | +0.100 | -0.033 [-0.100, +0.033] | +0.16 [-0.72, +0.83] | [-0.60, +0.73] | no / no / yes | -0.40 [-0.68, -0.05] | no | 1 / 1 | criterion shift, d' undetermined |
| adv: authority_claim | +0.000 | -0.300 | +0.150 [+0.069, +0.242] | +0.76 [+0.34, +1.30] | [+0.41, +1.22] | no / no / no | +0.38 [+0.17, +0.65] | no | 1 / 0.0352 | discrimination gain |
| adv: compliance_claim | +0.000 | -0.067 | +0.033 [+0.000, +0.086] | +0.18 [+0.00, +0.51] | [+0.00, +0.45] | no / yes / yes | +0.09 [+0.00, +0.25] | no | 1 / 1 | no detectable change, d' equivalent |
| adv: deadline_pressure | +0.033 | +0.067 | -0.017 [-0.069, +0.034] | +0.27 [-0.51, +0.84] | [-0.42, +0.75] | no / no / no | -0.34 [-0.61, +0.00] | no | 1 / 1 | inconclusive |
| adv: distraction_comment | -0.033 | +0.067 | -0.050 [-0.103, +0.000] | -0.47 [-1.17, +0.00] | [-1.05, -0.09] | no / no / no | +0.03 [-0.25, +0.37] | no | 1 / 1 | inconclusive |
| adv: fake_review_approval | +0.000 | -0.100 | +0.050 [+0.000, +0.103] | +0.27 [+0.00, +0.60] | [+0.08, +0.55] | no / no / yes | +0.14 [+0.00, +0.30] | no | 1 / 1 | inconclusive |
| adv: false_reassurance | -0.067 | -0.233 | +0.083 [-0.017, +0.177] | +0.15 [-0.65, +0.91] | [-0.52, +0.80] | no / no / no | +0.52 [+0.21, +0.91] | no | 1 / 0.109 | criterion shift, d' undetermined |
| adv: false_test_coverage | -0.100 | -0.300 | +0.100 [-0.017, +0.210] | +0.16 [-0.67, +0.97] | [-0.57, +0.81] | no / no / no | +0.68 [+0.35, +1.11] | no | 1 / 0.0352 | criterion shift, d' undetermined |
| adv: formal_verification | -0.067 | -0.433 | +0.183 [+0.069, +0.290] | +0.66 [-0.19, +1.48] | [-0.11, +1.36] | no / no / no | +0.78 [+0.43, +1.20] | no | 1 / 0.00293 | criterion shift, d' undetermined |
| adv: misleading_context | -0.067 | -0.367 | +0.150 [+0.034, +0.258] | +0.48 [-0.39, +1.36] | [-0.23, +1.22] | no / no / no | +0.69 [+0.39, +1.10] | no | 1 / 0.00977 | criterion shift, d' undetermined |
| adv: scope_limitation | -0.100 | -0.400 | +0.150 [+0.033, +0.267] | +0.41 [-0.50, +1.31] | [-0.34, +1.13] | no / no / no | +0.81 [+0.47, +1.23] | no | 1 / 0.00537 | criterion shift, d' undetermined |
| adv: security_camouflage | +0.033 | -0.233 | +0.133 [+0.052, +0.224] | +1.08 [+0.29, +1.72] | [+0.40, +1.61] | no / no / no | +0.06 [-0.30, +0.51] | no | 1 / 0.109 | discrimination gain |

## qwen3.5:4b+nothink

Clean: TPR 1.000, FPR 0.367, yes-rate 0.683, bAcc 0.817, d' 2.47, c -0.91

| Comparison vs clean | dTPR | dFPR | dbAcc [95% CI] | d' shift [95% CI] | d' 90% CI (TOST) | equivalent at +/-0.25 / 0.50 / 0.75 | c shift [95% CI] | bAcc equiv +/-0.05 | Holm McNemar vuln / safe | Reading |
|---|---|---|---|---|---|---|---|---|---|---|
| doc (benign comments) | -0.033 | +0.067 | -0.050 [-0.103, +0.000] | -0.65 [-1.20, +0.00] | [-1.10, -0.08] | no / no / no | +0.16 [-0.19, +0.43] | no | - | inconclusive |
| adversarial pooled, two-way bootstrap (PRIMARY) | -0.164 | -0.064 | -0.050 [-0.132, +0.033] | -0.63 [-1.12, -0.03] | [-1.02, -0.12] | no / no / no | +0.63 [+0.18, +1.11] | no | - | discrimination loss |
| adversarial pooled, pair-only bootstrap | -0.164 | -0.064 | -0.050 [-0.118, +0.017] | -0.63 [-1.03, -0.15] | [-0.95, -0.22] | no / no / no | +0.63 [+0.43, +0.79] | no | - | discrimination loss |
| adv: authorial_confidence | +0.000 | +0.300 | -0.150 [-0.241, -0.067] | -0.75 [-1.26, -0.34] | [-1.19, -0.41] | no / no / no | -0.37 [-0.63, -0.17] | no | 1 / 0.0391 | discrimination loss |
| adv: authority_claim | -0.100 | -0.167 | +0.033 [-0.052, +0.121] | -0.45 [-1.05, +0.46] | [-0.96, +0.28] | no / no / no | +0.70 [+0.26, +1.02] | no | 1 / 0.438 | criterion shift, d' undetermined |
| adv: compliance_claim | +0.000 | +0.033 | -0.017 [-0.081, +0.034] | -0.08 [-0.41, +0.18] | [-0.34, +0.16] | no / yes / yes | -0.04 [-0.20, +0.09] | no | 1 / 1 | no detectable change, d' equivalent |
| adv: deadline_pressure | -0.033 | +0.067 | -0.050 [-0.100, +0.000] | -0.65 [-1.17, +0.00] | [-1.09, -0.08] | no / no / no | +0.16 [-0.16, +0.43] | no | 1 / 1 | inconclusive |
| adv: distraction_comment | -0.100 | +0.267 | -0.183 [-0.293, -0.081] | -1.59 [-2.26, -0.75] | [-2.15, -0.89] | no / no / no | +0.14 [-0.40, +0.50] | no | 1 / 0.309 | discrimination loss |
| adv: fake_review_approval | +0.000 | -0.067 | +0.033 [-0.048, +0.117] | +0.18 [-0.26, +0.61] | [-0.17, +0.55] | no / no / yes | +0.09 [-0.13, +0.30] | no | 1 / 1 | inconclusive |
| adv: false_reassurance | -0.733 | -0.367 | -0.183 [-0.317, -0.033] | -0.93 [-1.76, -0.17] | [-1.61, -0.33] | no / no / no | +2.28 [+1.99, +2.56] | no | 5.72e-06 / 0.0117 | discrimination loss |
| adv: false_test_coverage | -0.167 | -0.300 | +0.067 [-0.050, +0.177] | -0.14 [-0.84, +0.89] | [-0.73, +0.72] | no / no / yes | +1.14 [+0.76, +1.61] | no | 0.625 / 0.0391 | criterion shift, d' undetermined |
| adv: formal_verification | -0.133 | -0.067 | -0.033 [-0.155, +0.081] | -0.91 [-1.64, +0.03] | [-1.53, -0.13] | no / no / no | +0.63 [+0.33, +0.86] | no | 1 / 1 | criterion shift, d' undetermined |
| adv: misleading_context | -0.100 | -0.100 | +0.000 [-0.097, +0.086] | -0.66 [-1.27, +0.25] | [-1.16, +0.08] | no / no / no | +0.60 [+0.09, +0.98] | no | 1 / 1 | criterion shift, d' undetermined |
| adv: scope_limitation | -0.533 | -0.333 | -0.100 [-0.233, +0.034] | -0.89 [-1.64, +0.08] | [-1.49, -0.08] | no / no / no | +1.78 [+1.41, +2.20] | no | 0.000336 / 0.0215 | criterion shift, d' undetermined |
| adv: security_camouflage | -0.067 | -0.033 | -0.017 [-0.086, +0.052] | -0.65 [-1.23, +0.20] | [-1.16, +0.10] | no / no / no | +0.41 [+0.00, +0.68] | no | 1 / 1 | inconclusive |

