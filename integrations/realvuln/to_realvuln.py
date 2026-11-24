"""Convert CommentInject v2 (data/cases.jsonl) into RealVuln target repos + ground truth.

RealVuln (https://github.com/kolega-ai/Real-Vuln-Benchmark) scores a scanner per target repo:
a directory tree of code plus ground-truth/{slug}/ground-truth.json (schema_version 1.0) whose
findings are real vulnerabilities (is_vulnerable: true) and false-positive traps (false).
CommentInject's matched pairs map onto that directly: the vulnerable twin is a finding, the
minimally fixed twin is a trap, and each comment condition is a separate target, so the
comment-robustness shift is the change in RealVuln's own TPR/FPR/F3 between the `clean` target
and each comment target.

Layout (28 targets = 14 conditions x 2 halves, 30 files each):
  {out}/targets/{slug}/{pair_id}.py           one file per case; neutral name, no label words
  {out}/ground-truth/{slug}/ground-truth.json
  {out}/case_map.csv                          slug,file,case_id,label (for the result adapter)

Each half holds exactly ONE twin of every pair (15 vulnerable + 15 fixed), so no target ever
contains both twins of a pair. This matters for RealVuln's LLM runners, which put a whole target
into one prompt (single-turn) or let the model browse it (agentic): with both twins side by side
the task would become "spot the difference". The vulnerable/fixed split is the same in every
condition, so `{cond}-a` differs from `clean-a` only by the comment.

Usage:
  python3 -I integrations/realvuln/to_realvuln.py --out OUT_DIR \
      [--repo-url URL] [--commit-sha SHA40]
The default repo_url/commit_sha are placeholders that pass RealVuln's validator; replace them with
the public mirror's values before proposing the targets upstream (see README.md).
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CASES = os.path.join(ROOT, "data", "cases.jsonl")

DATASET_VERSION = "2.0.0-rc2"
RV_BENCHMARK_VERSION = "3.1.1"      # RealVuln benchmark-manifest.json at commit 71a680a (2026-11-23)
GT_VERSION = "1.0.0"                # version of these CommentInject ground-truth files
PLACEHOLDER_URL = "https://github.com/OWNER/commentinject-v2-realvuln"
PLACEHOLDER_SHA = "0" * 40
SPLIT_SALT = "commentinject-v2-realvuln-split-v1"

# CommentInject CWE -> (vulnerability_class, acceptable_cwes, expected_category).
# Classes and CWE sets follow RealVuln's config/cwe-families.json where a family exists, and the
# class names RealVuln's own Python ground truth uses otherwise.
CWE_MAP = {
    "CWE-89":  ("sql_injection", ["CWE-89", "CWE-564", "CWE-943"], "injection"),
    "CWE-78":  ("command_injection", ["CWE-78", "CWE-77"], "injection"),
    "CWE-77":  ("command_injection", ["CWE-77", "CWE-78"], "injection"),
    "CWE-79":  ("xss", ["CWE-79", "CWE-80", "CWE-87"], "xss"),
    "CWE-22":  ("path_traversal", ["CWE-22", "CWE-23", "CWE-36"], "injection"),
    "CWE-798": ("hardcoded_credentials", ["CWE-798", "CWE-259"], "data_exposure"),
    "CWE-259": ("hardcoded_credentials", ["CWE-259", "CWE-798"], "data_exposure"),
    "CWE-327": ("weak_cryptography", ["CWE-327", "CWE-328"], "data_exposure"),
    "CWE-502": ("insecure_deserialization", ["CWE-502"], "injection"),
    "CWE-94":  ("code_injection", ["CWE-94", "CWE-95"], "injection"),
    "CWE-330": ("weak_prng", ["CWE-330", "CWE-338"], "other"),
    "CWE-611": ("xxe", ["CWE-611"], "injection"),
    "CWE-918": ("ssrf", ["CWE-918"], "injection"),
    "CWE-295": ("improper_certificate_validation", ["CWE-295"], "other"),
}


def load_cases(path=CASES):
    with open(path, encoding="utf-8") as f:
        cases = [json.loads(l) for l in f if l.strip()]
    for c in cases:
        if hashlib.sha256(c["code"].encode()).hexdigest() != c["sha256"]:
            sys.exit(f"sha256 mismatch for {c['case_id']}")
    return cases


def condition_slug(c):
    return c["condition"] if c["strategy"] == "none" else c["strategy"]


def vulnerable_in_half_a(pair_ids):
    """Deterministic balanced split: the first half of pairs (by salted hash) put the
    vulnerable twin in half a; the rest put the fixed twin there."""
    order = sorted(pair_ids, key=lambda p: hashlib.sha256(f"{SPLIT_SALT}:{p}".encode()).hexdigest())
    return set(order[: len(order) // 2])


def half_of(c, vuln_a):
    in_a = (c["label"] == 1) == (c["pair_id"] in vuln_a)
    return "a" if in_a else "b"


def target_slug(cond, half):
    return f"realvuln-commentinject-{cond.replace('_', '-')}-{half}"


def function_span(code):
    tree = ast.parse(code)
    fn = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if len(fn) != 1:
        raise ValueError("expected exactly one top-level function")
    return fn[0].name, fn[0].lineno, fn[0].end_lineno


def gt_finding(slug, c):
    vclass, cwes, category = CWE_MAP[c["cwe"]]
    name, start, end = function_span(c["code"])
    vuln = c["label"] == 1
    twin = "vulnerable twin" if vuln else "minimally fixed twin (false-positive trap)"
    return {
        "id": f"{slug}-{c['pair_id'].lower()}" if vuln else f"{slug}-fp-{c['pair_id'].lower()}",
        "is_vulnerable": vuln,
        "vulnerability_class": vclass,
        "primary_cwe": c["cwe"],
        "acceptable_cwes": cwes,
        "file": f"{c['pair_id']}.py",
        "location": {"start_line": start, "end_line": end, "function": name},
        "severity": "unrated",
        "expected_category": category,
        "evidence": {
            "source": "manual_review",
            "cve_id": None,
            "description": (
                f"CommentInject v2 {DATASET_VERSION} pair {c['pair_id']} ({c['cwe']}), {twin}; "
                f"comment condition '{condition_slug(c)}'. Label by construction of the matched pair "
                "(flaw pattern present only in the vulnerable twin; automated and independent model "
                "review; human review in progress)."
            ),
        },
        "commentinject": {"case_id": c["case_id"], "sha256": c["sha256"], "label": c["label"],
                          "condition": c["condition"], "strategy": c["strategy"]},
    }


def build(out, repo_url=PLACEHOLDER_URL, commit_sha=PLACEHOLDER_SHA, cases_path=CASES):
    cases = load_cases(cases_path)
    vuln_a = vulnerable_in_half_a({c["pair_id"] for c in cases})
    groups = {}
    for c in cases:
        groups.setdefault(target_slug(condition_slug(c), half_of(c, vuln_a)), []).append(c)
    rows = []
    for slug, members in sorted(groups.items()):
        members.sort(key=lambda c: c["pair_id"])
        tdir = os.path.join(out, "targets", slug)
        os.makedirs(tdir, exist_ok=True)
        for c in members:
            with open(os.path.join(tdir, f"{c['pair_id']}.py"), "w", encoding="utf-8", newline="\n") as f:
                f.write(c["code"] + "\n")
            rows.append((slug, f"{c['pair_id']}.py", c["case_id"], c["label"]))
        gt = {
            "schema_version": "1.0",
            "benchmark_version": RV_BENCHMARK_VERSION,
            "ground_truth_version": GT_VERSION,
            "repo_id": slug.removeprefix("realvuln-"),
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "type": 4,
            "language": "python",
            "framework": None,
            "authorship": "unknown",
            "authorship_model": None,
            "authorship_confidence": "low",
            "authorship_evidence": (
                "Short benchmark functions from CommentInject v1/v2 (matched vulnerable/fixed twins); "
                "authorship provenance to be stated by the dataset authors before upstream submission."
            ),
            "loc": sum(c["code"].count("\n") + 1 for c in members),
            "commentinject": {"dataset_version": DATASET_VERSION,
                              "condition": condition_slug(members[0]),
                              "half": slug.rsplit("-", 1)[1]},
            "findings": [gt_finding(slug, c) for c in members],
        }
        gdir = os.path.join(out, "ground-truth", slug)
        os.makedirs(gdir, exist_ok=True)
        with open(os.path.join(gdir, "ground-truth.json"), "w", encoding="utf-8") as f:
            json.dump(gt, f, indent=2, ensure_ascii=False)
            f.write("\n")
    with open(os.path.join(out, "case_map.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["slug", "file", "case_id", "label"])
        w.writerows(rows)
    return groups


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--repo-url", default=PLACEHOLDER_URL)
    ap.add_argument("--commit-sha", default=PLACEHOLDER_SHA)
    a = ap.parse_args(argv)
    groups = build(a.out, a.repo_url, a.commit_sha)
    n = sum(len(v) for v in groups.values())
    print(f"wrote {len(groups)} targets, {n} cases -> {a.out}")


if __name__ == "__main__":
    main()
