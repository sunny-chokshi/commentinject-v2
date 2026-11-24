"""Paid-model token probe for CommentInject v2, with a HARD spending cap (approved by Sunny: under $1).

Usage (keys come only from environment variables set by Sunny; this script never asks for or stores keys):
  python3 -I scripts/run_api.py --out results/api_probe/probe_<UTC>.jsonl --cap-usd 0.95 [--providers anthropic openai google] [--dry-run]
Safety: SDK retries disabled (max_retries=0 / attempts=1), 90 s timeout, any API error skips that model,
output must be a NEW file in results/api_probe/, cap is cumulative over all earlier probe files.

Probe design: 20 cases per model = 5 pairs x {vulnerable, safe} x {clean, authority_claim}, the same prompt as
the local runs. Models are tried cheapest first; a model is skipped if its WORST-CASE cost would breach the cap.
Before every call the script checks: spent_so_far + worst_case(this call) <= cap, where worst_case uses
the real input token estimate and max_output_tokens at list price. Actual cost is computed from the usage the API
returns (thinking/reasoning tokens bill as output). Results are EXPLORATORY pending human validation.
Prices: docs/COST_ESTIMATE_PAID_MODELS_2026-11-24.md (USD per 1M tokens, standard, read 2026-11-24 / cached 2026-11-03).
"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, REVIEW_PROMPT, load_jsonl, parse_verdict, parse_verdict_v1

MAX_OUT = 2000          # includes thinking/reasoning tokens
PAIRS = ["V01", "V04", "V10", "V22", "V27"]           # SQLi, path traversal, XXE (corrected), YAML, SSRF (corrected)
STRATS = ["none", "authority_claim"]
MODELS = [  # (provider, model id, $ in / 1M, $ out / 1M, env var)
    ("anthropic", "claude-haiku-5-5", 0.10, 0.50, "ANTHROPIC_API_KEY"),
    ("openai", "gpt-6-luna", 0.10, 0.50, "OPENAI_API_KEY"),
    ("google", "gemini-3.8-flash", 1.50, 7.50, "GEMINI_API_KEY"),      # Jan-2027 price used (higher, conservative)
    ("anthropic", "claude-sonnet-5-5", 2.00, 10.00, "ANTHROPIC_API_KEY"),
    ("openai", "gpt-6.1-terra", 1.00, 5.00, "OPENAI_API_KEY"),
]

def call(provider, model, prompt):
    """Returns (text, input_tokens, output_tokens). Output tokens include reasoning/thinking."""
    if provider == "anthropic":
        import anthropic
        r = anthropic.Anthropic(max_retries=0, timeout=90.0).messages.create(model=model, max_tokens=MAX_OUT, output_config={"effort": "low"},
                                                  messages=[{"role": "user", "content": prompt}])
        text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
        return text, r.usage.input_tokens, r.usage.output_tokens
    if provider == "openai":
        from openai import OpenAI
        r = OpenAI(max_retries=0, timeout=90.0).responses.create(model=model, input=prompt, max_output_tokens=MAX_OUT, reasoning={"effort": "low"})
        return r.output_text, r.usage.input_tokens, r.usage.output_tokens
    if provider == "google":
        from google import genai
        from google.genai import types
        client = genai.Client(http_options=types.HttpOptions(timeout=90_000, retry_options=types.HttpRetryOptions(attempts=1)))
        r = client.models.generate_content(model=model, contents=prompt,
                                                   config=types.GenerateContentConfig(max_output_tokens=MAX_OUT))
        u = r.usage_metadata
        out = (u.candidates_token_count or 0) + (getattr(u, "thoughts_token_count", 0) or 0)
        return r.text or "", u.prompt_token_count, out
    raise ValueError(provider)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="NEW file under results/api_probe/; an existing file is never overwritten")
    ap.add_argument("--cap-usd", type=float, default=0.95, help="cumulative cap across ALL results/api_probe/*.jsonl")
    ap.add_argument("--providers", nargs="+", default=["anthropic", "openai", "google"])
    ap.add_argument("--dry-run", action="store_true", help="select cases and print worst-case costs; no API calls")
    a = ap.parse_args()
    if a.cap_usd > 1.0: sys.exit("cap above the approved $1 - refusing")
    probe_dir = os.path.join(os.path.dirname(DATA), "results", "api_probe")
    if os.path.abspath(os.path.dirname(a.out)) != os.path.abspath(probe_dir): sys.exit(f"--out must be inside {probe_dir}")
    if os.path.exists(a.out) and os.path.getsize(a.out) > 0 and not a.dry_run: sys.exit(f"{a.out} exists and is not empty - choose a new file name")
    # corrected (Phase 2) dataset guard
    pairs = {p["pair_id"]: p for p in load_jsonl(os.path.join(DATA, "pairs.jsonl"))}
    if "feature_external_ges, True" not in pairs["V10"]["vulnerable_code"] or "allow_redirects=False" not in pairs["V27"]["safe_code"]:
        sys.exit("data/ is not the corrected Phase 2 dataset - refusing")
    import hashlib
    print("dataset: Phase 2 (corrected); data/cases.jsonl sha256", hashlib.sha256(open(os.path.join(DATA, "cases.jsonl"), "rb").read()).hexdigest()[:16])
    cases = [c for c in load_jsonl(os.path.join(DATA, "cases.jsonl"))
             if c["pair_id"] in PAIRS and c["condition"] in ("clean", "adversarial") and c["strategy"] in STRATS]
    assert len(cases) == 20, len(cases)
    est_in = lambda c: len(REVIEW_PROMPT.format(code=c["code"])) / 3.0 + 20      # generous token estimate
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    spent = 0.0   # cumulative over every earlier probe file, so re-running can never exceed the cap in total
    for fn in os.listdir(probe_dir) if os.path.isdir(probe_dir) else []:
        if fn.endswith(".jsonl") and os.path.getsize(os.path.join(probe_dir, fn)) > 0:
            spent += sum(r["cost_usd"] for r in load_jsonl(os.path.join(probe_dir, fn)))
    done = set()
    print(f"cap ${a.cap_usd:.2f} (cumulative); already spent ${spent:.4f}; retries disabled; timeout 90 s per call")
    with open(os.devnull if a.dry_run else a.out, "a") as f:   # dry run never creates the output file
        for prov, model, pin, pout, env in MODELS:
            worst_model = sum(est_in(c) * pin / 1e6 + MAX_OUT * pout / 1e6 for c in cases)
            if prov not in a.providers:
                print(f"skip {model}: provider not selected"); continue
            if not os.environ.get(env):
                print(f"skip {model}: {env} not set"); continue
            if a.dry_run:
                print(f"{model}: worst case for 20 calls ${worst_model:.3f}"); continue
            for c in cases:
                if (model, c["case_id"]) in done: continue
                worst = est_in(c) * pin / 1e6 + MAX_OUT * pout / 1e6
                if spent + worst > a.cap_usd:
                    print(f"STOP before {model} {c['case_id']}: spent ${spent:.4f} + worst ${worst:.4f} > cap"); return
                t = time.time()
                try:
                    text, tin, tout = call(prov, model, REVIEW_PROMPT.format(code=c["code"]))
                except Exception as e:
                    print(f"{model}: error {type(e).__name__}: {str(e)[:200]} - skipping model"); break
                cost = tin * pin / 1e6 + tout * pout / 1e6; spent += cost
                flagged, mode = parse_verdict(text)
                rec = {k: c[k] for k in ("case_id", "pair_id", "cwe", "variant", "label", "condition", "strategy", "sha256")}
                rec.update(provider=prov, model=model, flagged=flagged, parse_mode=mode, flagged_v1_parser=parse_verdict_v1(text),
                           response=text, input_tokens=tin, output_tokens=tout, cost_usd=round(cost, 6),
                           seconds=round(time.time() - t, 2), ts=time.strftime("%Y-%m-%dT%H:%M:%S"))
                f.write(json.dumps(rec) + "\n"); f.flush()
            print(f"{model}: done; total spent ${spent:.4f}")
    print(f"TOTAL SPENT ${spent:.4f} (cap ${a.cap_usd:.2f})")

if __name__ == "__main__":
    main()
