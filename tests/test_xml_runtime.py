"""Runtime exploit check for the XML pairs (V10, V25): the vulnerable twin must leak a local file through an
external entity on THIS interpreter, the safe twin must not. Usage: python3 -I tests/test_xml_runtime.py"""
import json, os, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pairs = {json.loads(l)["pair_id"]: json.loads(l) for l in open(os.path.join(ROOT, "data", "pairs.jsonl"))}
d = tempfile.mkdtemp(); secret = os.path.join(d, "s.txt"); open(secret, "w").write("TOPSECRET")
doc = f'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file://{secret}">]><r>&x;</r>'
def run(code, fn, arg):
    ns = {}; exec(code, ns)
    try:
        r = ns[fn](arg)
    except Exception as e:
        return f"error {type(e).__name__}"
    from lxml import etree
    txt = r.documentElement.toxml() if hasattr(r, "documentElement") else etree.tostring(r).decode()
    return "LEAK" if "TOPSECRET" in txt else "no leak"
fails = []
for pid, fn, arg in (("V10", "parse_xml", doc), ("V25", "load_xml", doc.encode())):
    v, s = run(pairs[pid]["vulnerable_code"], fn, arg), run(pairs[pid]["safe_code"], fn, arg)
    print(f"{pid}: vulnerable -> {v}; safe -> {s}")
    if v != "LEAK": fails.append(f"{pid} vulnerable twin does not leak")
    if s == "LEAK": fails.append(f"{pid} safe twin leaks")
print("FAIL " + "; ".join(fails) if fails else "PASS: XML pairs behave as labelled on " + sys.version.split()[0])
sys.exit(1 if fails else 0)
