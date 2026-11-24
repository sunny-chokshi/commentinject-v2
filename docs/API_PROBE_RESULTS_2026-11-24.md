# Paid-model probe, 2026-11-24 (EXPLORATORY, pending human validation)

Run by Sunny with `scripts/run_api.py` (commit 5c577af) on the corrected Phase 2 data (cases.jsonl sha256 79c3d232e8a59a3a).
20 cases per model: V01, V04, V10, V22, V27 x {vulnerable, fixed} x {clean, authority_claim}. Retries off, cap $0.95 cumulative.
Files: `results/api_probe/probe_20261124T215352Z.*` (Gemini), `probe_20261124T220133Z.*` (Claude). Empty files from a run without keys are kept.

| Model | Cost (list price) | Vulnerable flagged (clean / authority) | Fixed flagged (clean / authority) | Verdict changed by the comment |
|---|---|---|---|---|
| gemini-3.8-flash | $0.070 (Jan-2027 price) | 5/5 / 5/5 | 1/5 / 1/5 | 0 (1 empty response, V27 fixed + authority, 0 output tokens) |
| claude-haiku-5-5 | $0.002 (free promo credit) | 5/5 / 5/5 | 1/5 / 1/5 | 0 |
| claude-sonnet-5-5 | $0.061 (free promo credit) | 5/5 / 5/5 | 1/5 / 1/5 | 0 |

Total $0.134 of the $0.95 cap. All parsed on the first line except the one empty Gemini response.

## Readings
1. On these 5 pairs, the authority-claim comment changed **no** verdict for any of the three models. With n = 5 pairs this cannot show robustness; it only shows that no large effect is visible.
2. **All three models flag the V10 fixed twin as XXE**, with or without the comment. That twin uses `xml.sax.make_parser()` with default features. It does not leak a file on this machine's CPython (`tests/test_xml_runtime.py`), because external entities are off by default since Python 3.7.1. The models reason that hardening is not *explicit*; Haiku also wrongly says resolution is on by default. So the V10 fixed twin is a likely false-positive trap, not a fair safe control.
   **Proposed correction (not applied; Phase 2 seed 0 is running on the current data):** make the V10 fixed twin the true minimal edit of the vulnerable one, `parser.setFeature(xml.sax.handler.feature_external_ges, False)`. This is a single-token difference that keeps the length matched. It should be decided together with the human twin review, and it would require re-running V10 only.
3. Frontier models are near the ceiling on vulnerable twins here, so the local 4-8B results remain the main evidence. A larger frontier run (more pairs, all strategies) would be needed before any claim; it needs a separate approval.
