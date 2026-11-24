#!/usr/bin/env python3
"""Export CommentInject v2 cases as a promptfoo JSONL tests file (standard library only).

One promptfoo test per case. Each test carries:
  vars      code, case_id, label        (code fills {{code}} in review_prompt.j2; label is read by verdict.js)
  metadata  case_id, pair_id, cwe, variant, label, condition, strategy, sha256
            (so `promptfoo eval --filter-metadata condition=clean` etc. also works on the full file)

It also writes review_prompt.j2 from scripts/common.py:REVIEW_PROMPT, so the prompt is the
benchmark's prompt byte for byte ({code} -> {{code}}).

Usage (from the repo root):
  python3 -I integrations/promptfoo/export_tests.py                       # all 840 -> commentinject-code-review/tests.jsonl
  python3 -I integrations/promptfoo/export_tests.py --pairs V24 --out /tmp/x/tests.jsonl   # 28 cases
  python3 -I integrations/promptfoo/export_tests.py --conditions clean --strategies none --limit 10 --out ...
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from common import DATA, REVIEW_PROMPT, load_jsonl  # noqa: E402

EXAMPLE_DIR = os.path.join(HERE, "commentinject-code-review")
META_KEYS = ("case_id", "pair_id", "cwe", "variant", "label", "condition", "strategy", "sha256")


def csv_set(s):
    return {x.strip() for x in s.split(",") if x.strip()} if s else None


def select(cases, pairs=None, conditions=None, strategies=None, variants=None, limit=0):
    out = [c for c in cases
           if (pairs is None or c["pair_id"] in pairs)
           and (conditions is None or c["condition"] in conditions)
           and (strategies is None or c["strategy"] in strategies)
           and (variants is None or c["variant"] in variants)]
    return out[:limit] if limit else out


def to_test(c):
    return {
        "description": c["case_id"],
        "vars": {"code": c["code"], "case_id": c["case_id"], "label": c["label"]},
        "metadata": {k: c[k] for k in META_KEYS},
    }


def prompt_template():
    assert REVIEW_PROMPT.count("{code}") == 1 and "{{" not in REVIEW_PROMPT
    return REVIEW_PROMPT.replace("{code}", "{{code}}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", default=os.path.join(DATA, "cases.jsonl"))
    ap.add_argument("--out", default=os.path.join(EXAMPLE_DIR, "tests.jsonl"))
    ap.add_argument("--prompt-out", default=os.path.join(EXAMPLE_DIR, "review_prompt.j2"),
                    help="where to write the prompt template ('' to skip)")
    ap.add_argument("--pairs", help="comma-separated pair_ids, e.g. V01,V24")
    ap.add_argument("--conditions", help="comma-separated: clean,doc,adversarial")
    ap.add_argument("--strategies", help="comma-separated strategy names (none = clean/doc)")
    ap.add_argument("--variants", help="comma-separated: vulnerable,safe")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args(argv)
    cases = select(load_jsonl(a.cases), csv_set(a.pairs), csv_set(a.conditions),
                   csv_set(a.strategies), csv_set(a.variants), a.limit)
    if not cases:
        sys.exit("no cases match the subset flags")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(to_test(c), ensure_ascii=False) + "\n")
    if a.prompt_out:
        with open(a.prompt_out, "w", encoding="utf-8", newline="") as f:
            f.write(prompt_template())
    print(f"exported {len(cases)} tests -> {a.out}")
    return cases


if __name__ == "__main__":
    main()
