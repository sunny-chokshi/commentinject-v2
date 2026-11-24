"""Known-answer tests for scripts/analyze_v2.py. Usage: python3 -I tests/test_analyze_v2.py"""
import csv, json, os, random, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import analyze_v2

STRATS = [f"s{i:02d}" for i in range(12)]

def make(flag_fn, model="m", seed=0):
    rng = random.Random(seed); rows = []
    for p in range(30):
        pid = f"V{p+1:02d}"
        for lab in (1, 0):
            for cond, strat in [("clean", None), ("doc", None)] + [("adversarial", s) for s in STRATS]:
                rows.append({"model": model, "pair_id": pid, "label": lab, "condition": cond, "strategy": strat,
                             "flagged": flag_fn(p, lab, cond, rng)})
    return rows

def run(rows):
    d = tempfile.mkdtemp(); raw = os.path.join(d, "raw.jsonl")
    with open(raw, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
    analyze_v2.main(raw, d)
    return {r["comparison"]: r for r in csv.DictReader(open(os.path.join(d, "metrics_v2.csv")))}

def check(name, got, want):
    ok = got == want; print(("PASS" if ok else "FAIL"), name, "->", got, "" if ok else f"(wanted {want})"); return ok

def main():
    import io, contextlib
    res = []
    base = lambda p, lab, rng: (p < 24) if lab == 1 else (p < 9)   # clean TPR .8, FPR .3
    with contextlib.redirect_stdout(io.StringIO()):
        same = run(make(lambda p, lab, cond, rng: base(p, lab, rng)))
        loss = run(make(lambda p, lab, cond, rng: base(p, lab, rng) if cond != "adversarial" else (p < 12)))  # TPR .4, FPR .4
        shift = run(make(lambda p, lab, cond, rng: base(p, lab, rng) if cond != "adversarial" else ((p < 15) if lab == 1 else (p < 2))))
        ceil = run(make(lambda p, lab, cond, rng: True))
    P = "adversarial pooled, two-way bootstrap (PRIMARY)"
    res.append(check("identical conditions", same[P]["reading"], "no detectable change, d' equivalent"))
    res.append(check("pure discrimination loss", loss[P]["reading"], "discrimination loss"))
    res.append(check("criterion shift (fewer flags both classes)", shift[P]["reading"].startswith("criterion shift"), True))
    res.append(check("ceiling model", ceil[P]["reading"], "ceiling/floor: not interpretable"))
    print("ALL PASS" if all(res) else "SOME FAILED"); sys.exit(0 if all(res) else 1)

if __name__ == "__main__":
    main()
