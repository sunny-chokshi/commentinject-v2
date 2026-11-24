"""Adapter: RealVuln-layout scanner results on the CommentInject targets -> case_id,flagged.

Reads {scan_root}/{slug}/{scanner}/results.json (Semgrep-compatible JSON, the format RealVuln
stores for every scanner, LLM runners included) for the 28 targets written by to_realvuln.py, and
writes a predictions CSV that scripts/score_predictions.py turns into TPR/FPR, d'/c and TOST.

Modes:
  any  a case is flagged if the scanner reports anything in its file (CWE ignored). This is
       CommentInject's own binary task (VULNERABLE/SAFE).
  cwe  flagged only if a finding's CWE is in the case's acceptable_cwes and its line is within
       RealVuln's +/-10 tolerance of the function. This mirrors RealVuln's matcher (a finding
       with a wrong CWE on a vulnerable twin is a miss there).

Usage:
  python3 -I integrations/realvuln/results_to_predictions.py BUILD_DIR SCAN_ROOT SCANNER OUT.csv \
      [--mode any|cwe] [--model NAME]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re

LINE_TOLERANCE = 10  # RealVuln scorer/matcher.py DEFAULT_LINE_TOLERANCE


def _norm(path: str) -> str:
    path = path.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path.lstrip("/")


def read_findings(path: str) -> list[dict]:
    """Semgrep-format results -> [{file, line, cwes}] (all results, with or without CWE)."""
    with open(path) as f:
        data = json.load(f)
    out = []
    for r in data.get("results", []):
        raw = (r.get("extra", {}).get("metadata", {}) or {}).get("cwe", [])
        if isinstance(raw, str):
            raw = [raw]
        cwes = {m.group(1) for m in (re.match(r"(CWE-\d+)", str(x)) for x in raw) if m}
        out.append({"file": _norm(r.get("path", "")), "line": (r.get("start") or {}).get("line"),
                    "cwes": cwes})
    return out


def load_gt(build_dir: str, slug: str) -> dict:
    with open(os.path.join(build_dir, "ground-truth", slug, "ground-truth.json")) as f:
        return json.load(f)


def predict(build_dir: str, scan_root: str, scanner: str, mode: str = "any") -> list[dict]:
    with open(os.path.join(build_dir, "case_map.csv")) as f:
        cmap = list(csv.DictReader(f))
    slugs = sorted({r["slug"] for r in cmap})
    preds = []
    for slug in slugs:
        res = os.path.join(scan_root, slug, scanner, "results.json")
        if not os.path.exists(res):
            raise FileNotFoundError(res)
        findings = read_findings(res)
        gt = {g["file"]: g for g in load_gt(build_dir, slug)["findings"]}
        for row in (r for r in cmap if r["slug"] == slug):
            g = gt[row["file"]]
            # match on the file name: targets are flat, so a scanner run from a parent directory
            # (path "realvuln-commentinject-clean-a/V01.py") still maps correctly
            mine = [x for x in findings if x["file"] == row["file"] or x["file"].endswith("/" + row["file"])]
            if mode == "cwe":
                lo = g["location"]["start_line"] - LINE_TOLERANCE
                hi = g["location"]["end_line"] + LINE_TOLERANCE
                mine = [x for x in mine if x["cwes"] & set(g["acceptable_cwes"])
                        and (x["line"] is None or lo <= x["line"] <= hi)]
            preds.append({"case_id": row["case_id"], "flagged": bool(mine)})
    return preds


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("build_dir")
    ap.add_argument("scan_root")
    ap.add_argument("scanner")
    ap.add_argument("out_csv")
    ap.add_argument("--mode", choices=("any", "cwe"), default="any")
    ap.add_argument("--model", default=None)
    a = ap.parse_args(argv)
    preds = predict(a.build_dir, a.scan_root, a.scanner, a.mode)
    model = a.model or f"{a.scanner}-{a.mode}"
    os.makedirs(os.path.dirname(os.path.abspath(a.out_csv)), exist_ok=True)
    with open(a.out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "flagged", "model"])
        for p in sorted(preds, key=lambda p: p["case_id"]):
            w.writerow([p["case_id"], "true" if p["flagged"] else "false", model])
    print(f"{len(preds)} predictions ({sum(p['flagged'] for p in preds)} flagged) -> {a.out_csv}")


if __name__ == "__main__":
    main()
