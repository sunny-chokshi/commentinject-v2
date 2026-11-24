"""Tests for the CommentInject -> RealVuln converter and result adapter.

Stdlib only:  python3 -I integrations/realvuln/tests/test_realvuln.py   (or pytest)
The RealVuln-tooling tests need a local clone of kolega-ai/Real-Vuln-Benchmark; point
REALVULN_DIR at it, otherwise they are skipped. RealVuln's modules are imported from the clone
(validate_gt, parsers, scorer); nothing is installed.
"""
from __future__ import annotations

import collections
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
import bandit_to_semgrep  # noqa: E402
import results_to_predictions  # noqa: E402
import to_realvuln  # noqa: E402

RV = os.environ.get("REALVULN_DIR", "")
HAVE_RV = bool(RV) and os.path.exists(os.path.join(RV, "validate_gt.py"))
if HAVE_RV:
    sys.path.insert(0, RV)

LABEL_WORDS = re.compile(r"vuln|safe|fixed|secure|insecure|patch|trap|fp", re.I)


def semgrep_result(path, line, cwe, check="t.rule"):
    return {"check_id": check, "path": path, "start": {"line": line, "col": 1},
            "end": {"line": line, "col": 2},
            "extra": {"message": "m", "severity": "ERROR",
                      "metadata": {"cwe": [cwe] if cwe else [], "confidence": "high"}}}


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = cls.tmp.name
        cls.groups = to_realvuln.build(cls.out)
        cls.cases = to_realvuln.load_cases()
        cls.slugs = sorted(cls.groups)
        cls.gts = {s: json.load(open(os.path.join(cls.out, "ground-truth", s, "ground-truth.json")))
                   for s in cls.slugs}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def write_results(self, root, scanner, fn):
        """fn(slug, gt_finding) -> list of semgrep results for that file."""
        for s in self.slugs:
            d = os.path.join(root, s, scanner)
            os.makedirs(d, exist_ok=True)
            res = [r for g in self.gts[s]["findings"] for r in fn(s, g)]
            json.dump({"version": "1.0.0", "results": res}, open(os.path.join(d, "results.json"), "w"))


class TestConverter(Base):
    def test_shape(self):
        self.assertEqual(len(self.cases), 840)
        self.assertEqual(len(self.slugs), 28)
        for s in self.slugs:
            self.assertEqual(len(self.groups[s]), 30)
            self.assertEqual(len(os.listdir(os.path.join(self.out, "targets", s))), 30)

    def test_every_case_exactly_once_and_bytes_match(self):
        seen = collections.Counter()
        for s, members in self.groups.items():
            for c in members:
                seen[c["case_id"]] += 1
                text = open(os.path.join(self.out, "targets", s, f"{c['pair_id']}.py"), encoding="utf-8").read()
                self.assertEqual(text, c["code"] + "\n")
                self.assertEqual(hashlib.sha256(text[:-1].encode()).hexdigest(), c["sha256"])
        self.assertEqual(set(seen), {c["case_id"] for c in self.cases})
        self.assertEqual(set(seen.values()), {1})

    def test_one_twin_per_pair_balanced_and_same_split_in_every_condition(self):
        split = {}
        for s in self.slugs:
            members = self.groups[s]
            self.assertEqual(len({c["pair_id"] for c in members}), 30)
            self.assertEqual(sum(c["label"] for c in members), 15)
            self.assertEqual(len({to_realvuln.condition_slug(c) for c in members}), 1)
            half = s.rsplit("-", 1)[1]
            sig = frozenset((c["pair_id"], c["label"]) for c in members)
            split.setdefault(half, set()).add(sig)
        self.assertEqual({k: len(v) for k, v in split.items()}, {"a": 1, "b": 1})

    def test_no_label_words_in_paths(self):
        for s in self.slugs:
            for name in os.listdir(os.path.join(self.out, "targets", s)):
                self.assertRegex(name, r"^V\d\d\.py$")
            self.assertIsNone(LABEL_WORDS.search(s.removeprefix("realvuln-commentinject-")), s)

    def test_ground_truth_consistent_with_cases(self):
        by_id = {c["case_id"]: c for c in self.cases}
        for s, gt in self.gts.items():
            ids = [f["id"] for f in gt["findings"]]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertEqual(sum(f["is_vulnerable"] for f in gt["findings"]), 15)
            for f in gt["findings"]:
                c = by_id[f["commentinject"]["case_id"]]
                self.assertEqual(f["is_vulnerable"], c["label"] == 1)
                self.assertEqual(f["primary_cwe"], c["cwe"])
                self.assertIn(f["primary_cwe"], f["acceptable_cwes"])
                self.assertEqual(f["file"], f"{c['pair_id']}.py")
                n_lines = c["code"].count("\n") + 1
                self.assertTrue(1 <= f["location"]["start_line"] <= f["location"]["end_line"] <= n_lines)

    def test_case_map(self):
        rows = list(csv.DictReader(open(os.path.join(self.out, "case_map.csv"))))
        self.assertEqual(len(rows), 840)
        self.assertEqual(len({r["case_id"] for r in rows}), 840)


class TestAdapter(Base):
    def test_oracle_and_modes(self):
        with tempfile.TemporaryDirectory() as root:
            # vulnerable twins: correct CWE on the def line; fixed twins: a wrong-CWE finding
            self.write_results(root, "oracle", lambda s, g: [semgrep_result(
                g["file"], g["location"]["start_line"],
                g["primary_cwe"] if g["is_vulnerable"] else None)] if g["is_vulnerable"] else [])
            self.write_results(root, "noisy", lambda s, g: [semgrep_result(
                "./" + g["file"], g["location"]["start_line"],
                g["primary_cwe"] if g["is_vulnerable"] else "CWE-1")])
            label = {c["case_id"]: c["label"] == 1 for c in self.cases}
            for mode in ("any", "cwe"):
                p = results_to_predictions.predict(self.out, root, "oracle", mode)
                self.assertEqual(len(p), 840)
                self.assertTrue(all(x["flagged"] == label[x["case_id"]] for x in p))
            any_ = results_to_predictions.predict(self.out, root, "noisy", "any")
            cwe = results_to_predictions.predict(self.out, root, "noisy", "cwe")
            self.assertTrue(all(x["flagged"] for x in any_))
            self.assertTrue(all(x["flagged"] == label[x["case_id"]] for x in cwe))

    def test_bandit_converter(self):
        b = {"results": [{"filename": "./V07.py", "test_id": "B301", "test_name": "blacklist",
                          "issue_cwe": {"id": 502, "link": "x"}, "issue_severity": "MEDIUM",
                          "issue_confidence": "HIGH", "issue_text": "pickle", "line_number": 3,
                          "line_range": [3], "col_offset": 11, "end_col_offset": 30}], "errors": []}
        r = bandit_to_semgrep.convert(b)["results"][0]
        self.assertEqual((r["path"], r["start"]["line"], r["extra"]["metadata"]["cwe"]), ("V07.py", 3, ["CWE-502"]))
        self.assertEqual(r["extra"]["severity"], "WARNING")


@unittest.skipUnless(HAVE_RV, "set REALVULN_DIR to a local RealVuln clone")
class TestRealVulnTooling(Base):
    def test_validate_gt_passes(self):
        import validate_gt
        validate_gt.GT_DIR = Path(self.out) / "ground-truth"
        for s in self.slugs:
            errs = validate_gt.validate_gt(validate_gt.GT_DIR / s / "ground-truth.json")
            self.assertEqual([str(e) for e in errs], [], s)

    def test_loader_and_scorer(self):
        from parsers import get_parser
        from scorer.matcher import load_ground_truth, match_findings
        from scorer.metrics import compute_scorecard
        fam = json.load(open(os.path.join(RV, "config", "cwe-families.json")))
        with tempfile.TemporaryDirectory() as root:
            self.write_results(root, "oracle", lambda s, g: [semgrep_result(
                g["file"], g["location"]["start_line"], g["primary_cwe"])] if g["is_vulnerable"] else [])
            self.write_results(root, "all", lambda s, g: [semgrep_result(
                g["file"], g["location"]["start_line"], g["primary_cwe"])])
            self.write_results(root, "none", lambda s, g: [])
            for s in self.slugs:
                gt = load_ground_truth(os.path.join(self.out, "ground-truth", s, "ground-truth.json"))
                for scanner, want in (("oracle", (15, 0, 0, 15)), ("all", (15, 15, 0, 0)),
                                      ("none", (0, 0, 15, 15))):
                    f = get_parser(scanner).parse(os.path.join(root, s, scanner, "results.json"))
                    card = compute_scorecard(gt["repo_id"], scanner, "-", match_findings(f, gt), fam)
                    self.assertEqual((card.tp, card.fp, card.fn, card.tn), want, (s, scanner))


if __name__ == "__main__":
    unittest.main(verbosity=1)
