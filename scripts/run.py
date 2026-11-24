"""Run CommentInject v2 cases against local Ollama models. Resumable: re-running skips done cases.
Usage: python3 -I scripts/run.py --models qwen2.5-coder:7b deepseek-coder:6.7b --out results/pilot/raw.jsonl [--limit N]
Provider adapters for paid APIs are deliberately NOT included until Sunny approves a budget."""
import argparse, json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, REVIEW_PROMPT, load_jsonl, parse_verdict, parse_verdict_v1

OLLAMA = "http://localhost:11434"

def model_digest(model):
    with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=30) as r:
        for m in json.loads(r.read())["models"]:
            if m["name"] == model:
                return m["digest"]
    raise SystemExit(f"model not pulled: {model}")

def query(model, code, think=None, seed=0):
    payload = {"model": model, "prompt": REVIEW_PROMPT.format(code=code), "stream": False,
               "options": {"temperature": 0, "seed": seed}}
    if think is not None:
        payload["think"] = think  # Ollama: disable hidden reasoning on thinking models
    body = json.dumps(payload).encode()
    req = urllib.request.Request(OLLAMA + "/api/generate", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["response"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--case-ids", help="file with one case_id per line; run only these (targeted re-runs)")
    ap.add_argument("--no-think", action="store_true",
                    help="send think=false (for reasoning models); rows are labelled '<model>+nothink'")
    a = ap.parse_args()
    cases = load_jsonl(os.path.join(DATA, "cases.jsonl"))
    if a.limit: cases = cases[:a.limit]
    if a.case_ids:
        keep = {l.strip() for l in open(a.case_ids) if l.strip()}
        cases = [c for c in cases if c["case_id"] in keep]
    done = set()
    if os.path.exists(a.out):
        done = {(r["model"], r["case_id"]) for r in load_jsonl(a.out)}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "a") as f:
        for model in a.models:
            digest = model_digest(model)
            label = model + "+nothink" if a.no_think else model
            todo = [c for c in cases if (label, c["case_id"]) not in done]
            print(f"{label} {digest[:12]}: {len(todo)} to run", flush=True)
            for i, c in enumerate(todo, 1):
                t = time.time()
                resp = query(model, c["code"], False if a.no_think else None, a.seed)
                flagged, mode = parse_verdict(resp)
                rec = {k: c[k] for k in ("case_id", "pair_id", "cwe", "variant", "label", "condition", "strategy", "sha256")}
                rec.update(model=label, model_digest=digest, think=(False if a.no_think else None), seed=a.seed, flagged=flagged, parse_mode=mode,
                           flagged_v1_parser=parse_verdict_v1(resp), response=resp,
                           seconds=round(time.time() - t, 2), ts=time.strftime("%Y-%m-%dT%H:%M:%S"))
                f.write(json.dumps(rec) + "\n"); f.flush()
                if i % 50 == 0: print(f"  {label} {i}/{len(todo)}", flush=True)
    print("done", flush=True)

if __name__ == "__main__":
    main()
