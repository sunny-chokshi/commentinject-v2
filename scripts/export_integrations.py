"""Export v2 cases into the two framework integrations (no framework install needed to export).

Both integrations read the same case-level JSONL (one record per case, raw fields, no prompt baked
in), so the review prompt is applied in exactly one place per framework and stays identical to
scripts/common.py REVIEW_PROMPT (tests in each integration check this).

  inspect: integrations/inspect_evals/commentinject/data/commentinject_v2.jsonl
  garak:   integrations/garak/commentinject_garak/data/commentinject_v2.jsonl

Usage: python3 -I scripts/export_integrations.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, ROOT, load_jsonl

FIELDS = ("case_id", "pair_id", "cwe", "variant", "label", "condition", "strategy", "code", "sha256")
TARGETS = (
    os.path.join(ROOT, "integrations", "inspect_evals", "commentinject", "data", "commentinject_v2.jsonl"),
    os.path.join(ROOT, "integrations", "garak", "commentinject_garak", "data", "commentinject_v2.jsonl"),
)

cases = load_jsonl(os.path.join(DATA, "cases.jsonl"))
for path in TARGETS:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps({k: c[k] for k in FIELDS}, ensure_ascii=False) + "\n")
    print("exported", len(cases), "->", os.path.relpath(path, ROOT))
