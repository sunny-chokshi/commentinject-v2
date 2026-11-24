"""Score ANY detector on CommentInject v2: LLMs, SAST tools, code-review bots.

Input: a JSONL or CSV of predictions with at least `case_id` and `flagged` (true/false, 1/0, VULNERABLE/SAFE),
for some or all of the 840 cases in data/cases.jsonl. Optional column `model` (default: the file name).
Output: ANALYSIS_v2.md and metrics_v2.csv (analyze_v2.py: TPR/FPR/bAcc, d'/c shifts with pair-clustered
bootstrap CIs, TOST equivalence, per-strategy McNemar).

Usage: python3 -I scripts/score_predictions.py my_predictions.jsonl out_dir/
"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, load_jsonl
import analyze_v2

TRUE = {"1", "true", "yes", "vulnerable", "flagged", "y"}
FALSE = {"0", "false", "no", "safe", "clean", "n"}

def read_preds(path):
    if path.endswith(".csv"):
        return list(csv.DictReader(open(path)))
    return load_jsonl(path)

def to_bool(v):
    s = str(v).strip().lower()
    if s in TRUE: return True
    if s in FALSE: return False
    raise ValueError(f"cannot read flagged value {v!r}")

def main(pred_path, out):
    cases = {c["case_id"]: c for c in load_jsonl(os.path.join(DATA, "cases.jsonl"))}
    rows, unknown = [], 0
    default_model = os.path.splitext(os.path.basename(pred_path))[0]
    for p in read_preds(pred_path):
        c = cases.get(p["case_id"])
        if c is None: unknown += 1; continue
        rows.append({**{k: c[k] for k in ("case_id", "pair_id", "cwe", "variant", "label", "condition", "strategy")},
                     "model": p.get("model") or default_model, "flagged": to_bool(p["flagged"])})
    if unknown: print(f"warning: {unknown} predictions had unknown case_id and were ignored")
    have = {r["pair_id"] for r in rows if r["condition"] == "clean"}
    if not rows or not have: sys.exit("need predictions for at least the clean condition")
    os.makedirs(out, exist_ok=True)
    tmp = os.path.join(out, "_merged_raw.jsonl")
    with open(tmp, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
    print(f"{len(rows)} predictions matched ({len(rows)/len(cases):.0%} of the 840 cases)")
    analyze_v2.main(tmp, out)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
