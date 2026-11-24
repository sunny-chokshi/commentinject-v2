"""Run a local, non-LLM SAST tool over the 28 CommentInject RealVuln targets (all 840 cases) and
score it both ways: with CommentInject's scorer (d'/c) and, optionally, RealVuln's own scorer.

  python3 -I integrations/realvuln/run_sast_baseline.py --tool bandit --bin /path/to/bandit \
      --work /scratch/dir --out results/sast_baselines/bandit [--realvuln-dir /path/to/clone]
  python3 -I integrations/realvuln/run_sast_baseline.py --tool semgrep --bin /path/to/semgrep \
      --semgrep-config rules.yaml --work /scratch/dir --out results/sast_baselines/semgrep

--work must be outside any git checkout (semgrep honours .gitignore). The scanners run with
cwd = each target directory, so result paths are repo-relative as RealVuln expects.
--realvuln-dir imports RealVuln's validate_gt, parsers and scorer from a local clone (run this
script with python -I; nothing from the clone is installed).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import bandit_to_semgrep  # noqa: E402
import results_to_predictions  # noqa: E402
import to_realvuln  # noqa: E402


def scan(tool, binary, target_dir, out_json, semgrep_config=None):
    env = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/tmp"), "LANG": "C.UTF-8"}
    if tool == "bandit":
        raw = out_json + ".bandit.json"
        p = subprocess.run([binary, "-r", ".", "-f", "json", "-o", raw, "-q"], cwd=target_dir,
                           env=env, capture_output=True, text=True)
        if p.returncode not in (0, 1) or not os.path.exists(raw):
            raise RuntimeError(f"bandit failed in {target_dir}: {p.stderr[-500:]}")
        with open(raw) as f:
            data = bandit_to_semgrep.convert(json.load(f))
        with open(out_json, "w") as f:
            json.dump(data, f, indent=1)
        os.remove(raw)
    elif tool == "semgrep":
        env["SEMGREP_SEND_METRICS"] = "off"
        p = subprocess.run([binary, "scan", "--config", semgrep_config, "--json", "--metrics", "off",
                            "--disable-version-check", "--no-git-ignore", "-o", out_json, "."],
                           cwd=target_dir, env=env, capture_output=True, text=True)
        if p.returncode not in (0, 1) or not os.path.exists(out_json):
            raise RuntimeError(f"semgrep failed in {target_dir}: {p.stderr[-800:]}")
    else:
        raise ValueError(tool)


def realvuln_scores(rv_dir, build, scan_root, scanner):
    sys.path.insert(0, rv_dir)
    import validate_gt  # RealVuln
    from parsers import get_parser
    from scorer.matcher import load_ground_truth, match_findings
    from scorer.metrics import compute_scorecard
    from pathlib import Path
    validate_gt.GT_DIR = Path(build) / "ground-truth"
    with open(os.path.join(rv_dir, "config", "cwe-families.json")) as f:
        fam = json.load(f)
    rows = []
    for slug in sorted(os.listdir(os.path.join(build, "ground-truth"))):
        gtp = os.path.join(build, "ground-truth", slug, "ground-truth.json")
        errs = validate_gt.validate_gt(Path(gtp))
        if errs:
            raise SystemExit(f"RealVuln validate_gt failed for {slug}: {[str(e) for e in errs]}")
        gt = load_ground_truth(gtp)
        findings = get_parser(scanner).parse(os.path.join(scan_root, slug, scanner, "results.json"))
        card = compute_scorecard(gt["repo_id"], scanner, "-", match_findings(findings, gt), fam)
        rows.append({"target": slug, "tp": card.tp, "fp": card.fp, "fn": card.fn, "tn": card.tn,
                     "tpr": round(card.tpr, 4), "fpr": round(card.fpr, 4),
                     "precision": round(card.precision, 4), "f3_score": card.f3_score})
    return rows


def verdict_changes(pred_csv):
    """Per condition: how many of the 60 cases change verdict relative to the same twin in clean."""
    with open(pred_csv) as f:
        p = {r["case_id"]: r["flagged"] == "true" for r in csv.DictReader(f)}
    cases = to_realvuln.load_cases()
    clean = {(c["pair_id"], c["variant"]): p[c["case_id"]] for c in cases if c["condition"] == "clean"}
    ch, n = defaultdict(int), defaultdict(int)
    for c in cases:
        k = to_realvuln.condition_slug(c)
        n[k] += 1
        ch[k] += p[c["case_id"]] != clean[(c["pair_id"], c["variant"])]
    return {k: (ch[k], n[k]) for k in n}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", choices=("bandit", "semgrep"), required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--semgrep-config")
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--realvuln-dir")
    a = ap.parse_args(argv)

    build = os.path.join(a.work, "build")
    if os.path.exists(build):
        shutil.rmtree(build)
    to_realvuln.build(build)
    scan_root = os.path.join(a.work, "scan-results")
    for slug in sorted(os.listdir(os.path.join(build, "targets"))):
        d = os.path.join(scan_root, slug, a.tool)
        os.makedirs(d, exist_ok=True)
        scan(a.tool, a.bin, os.path.join(build, "targets", slug), os.path.join(d, "results.json"),
             a.semgrep_config)
    os.makedirs(a.out, exist_ok=True)
    raw_dir = os.path.join(a.out, "raw_scan_results")
    if os.path.exists(raw_dir):
        shutil.rmtree(raw_dir)
    shutil.copytree(scan_root, raw_dir)

    summary = {"tool": a.tool, "modes": {}}
    for mode, sub in (("any", ""), ("cwe", "cwe_matched")):
        out = os.path.join(a.out, sub) if sub else a.out
        os.makedirs(out, exist_ok=True)
        pred = os.path.join(out, f"predictions_{a.tool}_{mode}.csv")
        results_to_predictions.main([build, scan_root, a.tool, pred, "--mode", mode,
                                     "--model", f"{a.tool}-{mode}"])
        subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts", "score_predictions.py"),
                        pred, out], check=True)
        summary["modes"][mode] = {"verdict_changes_vs_clean": {k: f"{c}/{n}" for k, (c, n) in
                                                               sorted(verdict_changes(pred).items())}}
    if a.realvuln_dir:
        rows = realvuln_scores(a.realvuln_dir, build, scan_root, a.tool)
        with open(os.path.join(a.out, "realvuln_scores.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        summary["realvuln_validate_gt"] = f"{len(rows)} targets, 0 errors"
    with open(os.path.join(a.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
