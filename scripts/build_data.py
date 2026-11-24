"""Build data/pairs.jsonl and data/cases.jsonl from pairs_def.py and CommentInject v1 samples.
Usage: python3 -I scripts/build_data.py /path/to/CommentInject_release/data/samples.jsonl"""
import json, os, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, load_jsonl, comment_block, strip_comments
from pairs_def import PAIRS, VULN_OVERRIDES

def main(v1_samples):
    v1 = {s["id"]: s for s in load_jsonl(v1_samples)}
    strategies = load_jsonl(os.path.join(DATA, "strategies.jsonl"))
    pairs = []
    for pid, doc, safe in PAIRS:
        s = v1[pid]
        vuln, why = VULN_OVERRIDES.get(pid, (s["code"], ""))
        pairs.append({"pair_id": pid, "cwe": s["cwe"], "name": s["name"],
                      "vulnerable_code": vuln, "safe_code": safe, "doc_comment": doc,
                      "v1_identical": pid not in VULN_OVERRIDES, "departure_reason": why})
    assert len(pairs) == 30 and {p["pair_id"] for p in pairs} == set(v1)
    with open(os.path.join(DATA, "pairs.jsonl"), "w") as f:
        for p in pairs: f.write(json.dumps(p) + "\n")
    cases = []
    for p in pairs:
        for variant in ("vulnerable", "safe"):
            code = p[f"{variant}_code"]
            conds = [("clean", "none", code),
                     ("doc", "none", comment_block(p["doc_comment"]) + code)]
            conds += [("adversarial", st["strategy"], st["comment"] + "\n" + code) for st in strategies]
            for cond, strat, text in conds:
                assert strip_comments(text) == strip_comments(code)
                cid = f'{p["pair_id"]}-{variant[0]}-{cond}-{strat}'
                cases.append({"case_id": cid, "pair_id": p["pair_id"], "cwe": p["cwe"], "variant": variant,
                              "label": 1 if variant == "vulnerable" else 0, "condition": cond,
                              "strategy": strat, "code": text,
                              "sha256": hashlib.sha256(text.encode()).hexdigest()})
    with open(os.path.join(DATA, "cases.jsonl"), "w") as f:
        for c in cases: f.write(json.dumps(c) + "\n")
    print(f"pairs={len(pairs)} cases={len(cases)} (stripping maps every case to its clean twin: checked)")

if __name__ == "__main__":
    main(sys.argv[1])
