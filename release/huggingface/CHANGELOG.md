# Changelog

## 2.0.0-rc2 (unreleased, 2026-11-24)
- **V10 fixed twin** is now the one-token minimal edit of the vulnerable twin: `parser.setFeature(xml.sax.handler.feature_external_ges, False)` (was: the default parser, with no explicit setting). Reason: in the paid-model probe, all three frontier models flagged the old fixed twin as XXE because hardening was not explicit, so it was not a fair safe control. Exploit-tested on CPython 3.14.6 / expat 2.8.2: vulnerable leaks a local file through a general external entity, a parameter entity and an external DTD subset; fixed leaks through none (`tests/test_xml_runtime.py`, `docs/API_PROBE_RESULTS_2026-11-24.md`).
- Only the 14 `V10-s-*` cases changed (sha256); all other 826 cases are byte-identical. Phase 2 seed 0 on rc1 data is kept unchanged (tag `phase2-seed0-2026-11-24`); the 14 cases are re-run with the same models (same digests), seed, prompt and settings into `results/phase2/raw_seed0_v10fix.jsonl`.
- `scripts/run.py --case-ids FILE` for targeted re-runs.

## 2.0.0-rc1 (unreleased, 2026-11-24)
- Added a matched, minimally fixed twin for each of the 30 v1 vulnerable functions.
- Added a `doc` condition with neutral purpose comments, to measure the cost of stripping comments. 840 cases in total.
- **Pairs that differ from v1** (v1 itself is unchanged):
  - **V10:** the v1 `xml.etree.ElementTree.fromstring` is not exploitable on CPython ≥ 3.7.1 with expat ≥ 2.4.1. v2 uses `xml.sax` with `feature_external_ges` enabled, which is verified to leak local files. The fix uses the default minidom parser.
  - **V15:** renamed `run_user_code(code_string)` to `run_user_action(action)` in both twins, because the old name biased both.
  - **V30:** renamed `secure_fetch` to `fetch_resource` in both twins, and put `timeout=10` in both.
  - **V27:** added `timeout=10` to the vulnerable twin. The fix now also rejects non-443 ports and disables redirects (the earlier fix was bypassable through redirects).
- Fixed-twin changes (not in v1): V23 has a distinct +/- evaluator instead of a copy of V08's; V24 keeps `user_id`; V25 drops the redundant `no_network`.
- Doc-comment changes (not in v1): V07 says where the input comes from; V28 no longer implies a trusted caller.
- Analysis: `analyze_v2.py` adds TOST equivalence, a pair-clustered and two-way bootstrap, per-strategy SDT and a ceiling rule. `analyze.py` is kept for the Phase 1 record.
- Tools: `score_predictions.py` scores any detector; `run_api.py` is the capped paid-model probe; Inspect and garak integrations.
- Erratum candidate for v1: V10, drafted in `docs/PROPOSED_DATASET_CORRECTIONS_2026-11-24.md`. **Not published.**
