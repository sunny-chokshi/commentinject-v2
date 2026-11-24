#!/usr/bin/env python3
"""Convert a promptfoo eval output (JSON from `promptfoo eval -o results.json`) into the
case_id,flagged CSV that scripts/score_predictions.py reads (standard library only).

For every result row the verdict comes from verdict.js (namedScores.flagged). The script
re-parses the raw model output with scripts/common.py:parse_verdict and stops if the two
disagree, so the JavaScript and Python parsers are checked on every real reply.
Rows that errored (no model output) are skipped and counted. A reply with no verdict is
written as flagged=false (the benchmark's primary-metric convention) with parse_mode=unparsed.

Usage:
  python3 -I integrations/promptfoo/to_predictions_csv.py results.json preds.csv
  python3 -I scripts/score_predictions.py preds.csv out_dir/
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from common import parse_verdict  # noqa: E402

FIELDS = ("case_id", "flagged", "model", "parse_mode", "response")


def result_rows(doc):
    res = doc.get("results", doc)
    rows = res.get("results") if isinstance(res, dict) else res
    if not isinstance(rows, list):
        raise ValueError("not a promptfoo eval output: expected results.results to be a list")
    return rows


def named(row, key):
    for src in (row.get("namedScores"), (row.get("gradingResult") or {}).get("namedScores")):
        if isinstance(src, dict) and key in src:
            return src[key]
    for comp in (row.get("gradingResult") or {}).get("componentResults") or []:
        ns = comp.get("namedScores") or {}
        if key in ns:
            return ns[key]
    return None


def convert(doc):
    out, errors = [], 0
    for row in result_rows(doc):
        vars_ = row.get("vars") or (row.get("testCase") or {}).get("vars") or {}
        case_id = vars_.get("case_id")
        if not case_id:
            raise ValueError("result row without vars.case_id; was tests.jsonl made by export_tests.py?")
        resp = row.get("response") or {}
        output = resp.get("output")
        if row.get("failureReason") == 2 or resp.get("error") or output is None:  # 2 = ERROR, 1 = assert fail
            errors += 1
            continue
        flagged_py, mode = parse_verdict(str(output))
        flagged_py = bool(flagged_py)  # unparsed counts as not flagged
        js = named(row, "flagged")
        if js is not None and bool(js) != flagged_py:
            raise ValueError(f"{case_id}: verdict.js says flagged={bool(js)}, parse_verdict says {flagged_py}")
        provider = row.get("provider") or {}
        model = provider.get("label") or provider.get("id") or ""
        out.append({"case_id": case_id, "flagged": str(flagged_py).lower(), "model": model,
                    "parse_mode": mode, "response": output})
    return out, errors


def main(src, dst):
    with open(src, encoding="utf-8") as f:
        rows, errors = convert(json.load(f))
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} predictions -> {dst}" + (f" ({errors} errored rows skipped)" if errors else ""))
    return rows, errors


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
