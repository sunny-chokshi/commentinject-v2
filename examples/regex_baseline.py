"""Worked example for adopters: a comment-blind regex 'SAST' baseline.
It writes predictions in the format score_predictions.py expects, so you can copy it for your own tool.
    python3 -I examples/regex_baseline.py > /tmp/regex_preds.csv
    python3 -I scripts/score_predictions.py /tmp/regex_preds.csv /tmp/regex_out
Because it drops comment lines before matching, adversarial comments cannot move it: its d'/c shifts are 0.
It also shows why low recall (TPR ~0.47) is not the point here: the benchmark measures how comments MOVE a detector."""
import csv, json, os, re, sys
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cases.jsonl")
PAT = re.compile(r"shell=True|os\.system|pickle|eval\(|exec\(|verify=False|md5|random\.randint|\+ username|"
                 r"yaml\.load\(|feature_external_ges, True|resolve_entities=True")
w = csv.writer(sys.stdout); w.writerow(["case_id", "flagged", "model"])
for line in open(DATA):
    c = json.loads(line)
    code = "\n".join(l for l in c["code"].splitlines() if not l.lstrip().startswith("#"))
    w.writerow([c["case_id"], "VULNERABLE" if PAT.search(code) else "SAFE", "regex-baseline"])
