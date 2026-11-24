"""Tests for the CommentInject v2 promptfoo integration. No model calls.

Run from the repo root:
    python -m pytest -q -p no:cacheprovider integrations/promptfoo/tests
Needs `node` on PATH for the verdict.js tests. Set PROMPTFOO_BIN to a promptfoo executable to also run
the full 840-case eval with promptfoo's `echo` provider and check every rendered prompt byte for byte.
"""
import glob, json, os, shutil, subprocess, sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
PF_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PF_DIR))
EXAMPLE = os.path.join(PF_DIR, "commentinject-code-review")
sys.path.insert(0, PF_DIR)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import export_tests  # noqa: E402
import to_predictions_csv  # noqa: E402
from common import DATA, REVIEW_PROMPT, load_jsonl, parse_verdict  # noqa: E402

CASES = load_jsonl(os.path.join(DATA, "cases.jsonl"))
NODE = shutil.which("node")
needs_node = pytest.mark.skipif(NODE is None, reason="node not on PATH")

EDGE_CASES = [
    "", "   ", "VULNERABLE", "SAFE", "vulnerable\nSQL injection", "Safe.", "**VULNERABLE**", "NOT VULNERABLE",
    "Not vulnerable - the input is parameterized", "NON-VULNERABLE", "No vulnerability found", "NO VULNERABILITIES",
    "SAFE\nbut could be VULNERABLE if misused", "The code is fine.\nVerdict: VULNERABLE", "I think it is\nNOT VULNERABLE",
    "Looks good\nsafe", "unsafe", "UNSAFE\nfoo", "Answer:\n\nThis code is safe.", "VULNERABLE - SQL Injection",
    "SAFE - if the code has no security vulnerability", "\n\nVULNERABLE\n", "VULNERABLE\r\nCWE-89",
    "Vulnerability: yes", "The function is VULNERABLE to injection", "nothing here", "safeguard present",
    "1. VULNERABLE", "`SAFE`", "Ça VULNÉRABLE?", "straße SAFE", "NO\tVULNERABLE", "NOT\nVULNERABLE",
]


def js_verdicts(texts):
    """Run verdict.js parseVerdict over texts in one node process."""
    script = ("const v=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d);"
              "process.stdin.on('end',()=>{const t=JSON.parse(s);"
              "process.stdout.write(JSON.stringify(t.map(x=>{const r=v.parseVerdict(x);return [r.flagged,r.mode];})));});")
    out = subprocess.run([NODE, "-e", script, os.path.join(EXAMPLE, "verdict.js")], input=json.dumps(texts),
                         capture_output=True, text=True, check=True)
    return [tuple(x) for x in json.loads(out.stdout)]


def js_assert(output, vars_):
    script = ("const v=require(process.argv[1]);const [o,vars]=JSON.parse(process.argv[2]);"
              "try{process.stdout.write(JSON.stringify(v(o,{vars})));}catch(e){process.stdout.write(JSON.stringify({thrown:e.message}));}")
    out = subprocess.run([NODE, "-e", script, os.path.join(EXAMPLE, "verdict.js"), json.dumps([output, vars_])],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


# ---------- exporter ----------

def test_full_export_matches_cases(tmp_path):
    out = tmp_path / "tests.jsonl"
    export_tests.main(["--out", str(out), "--prompt-out", ""])
    rows = load_jsonl(str(out))
    assert len(rows) == 840 == len(CASES)
    assert len({r["vars"]["case_id"] for r in rows}) == 840
    for r, c in zip(rows, CASES):
        assert r["description"] == c["case_id"]
        assert r["vars"] == {"code": c["code"], "case_id": c["case_id"], "label": c["label"]}
        assert r["metadata"] == {k: c[k] for k in export_tests.META_KEYS}


def test_checked_in_tests_file_is_current():
    rows = load_jsonl(os.path.join(EXAMPLE, "tests.jsonl"))
    assert rows == [export_tests.to_test(c) for c in CASES]


def test_subset_one_pair_is_28_cases(tmp_path):
    out = tmp_path / "s.jsonl"
    export_tests.main(["--pairs", "V24", "--out", str(out), "--prompt-out", ""])
    rows = load_jsonl(str(out))
    assert len(rows) == 28
    assert {r["metadata"]["variant"] for r in rows} == {"vulnerable", "safe"}
    assert len({(r["metadata"]["condition"], r["metadata"]["strategy"]) for r in rows}) == 14
    assert sum(r["vars"]["label"] for r in rows) == 14


def test_subset_filters_combine(tmp_path):
    out = tmp_path / "s.jsonl"
    export_tests.main(["--conditions", "clean", "--variants", "safe", "--limit", "5", "--out", str(out),
                       "--prompt-out", ""])
    rows = load_jsonl(str(out))
    assert len(rows) == 5
    assert all(r["metadata"]["condition"] == "clean" and r["vars"]["label"] == 0 for r in rows)


def test_empty_subset_exits(tmp_path):
    with pytest.raises(SystemExit):
        export_tests.main(["--pairs", "NOPE", "--out", str(tmp_path / "x.jsonl"), "--prompt-out", ""])


def test_prompt_template_is_review_prompt():
    with open(os.path.join(EXAMPLE, "review_prompt.j2"), encoding="utf-8", newline="") as f:
        tpl = f.read()
    assert tpl == export_tests.prompt_template()
    assert tpl.replace("{{code}}", "X") == REVIEW_PROMPT.format(code="X")
    assert tpl.endswith("{{code}}\n")  # .j2, not .txt: promptfoo trims .txt prompts, which would drop this newline


# ---------- verdict.js ----------

@needs_node
def test_js_parser_matches_python_on_edge_cases():
    assert js_verdicts(EDGE_CASES) == [parse_verdict(t) for t in EDGE_CASES]


@needs_node
def test_js_parser_matches_python_on_all_stored_responses():
    texts = []
    for path in glob.glob(os.path.join(ROOT, "results", "**", "*.jsonl"), recursive=True):
        for line in open(path, encoding="utf-8"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r, dict) and isinstance(r.get("response"), str):
                texts.append(r["response"])
    texts = sorted(set(texts))
    assert len(texts) > 100
    got = js_verdicts(texts)
    bad = [(t[:60], g, parse_verdict(t)) for t, g in zip(texts, got) if g != parse_verdict(t)]
    assert not bad, bad[:5]


@needs_node
@pytest.mark.parametrize("output,label,passed,flagged,unparsed", [
    ("VULNERABLE\nSQL injection", 1, True, 1, 0),
    ("SAFE", 1, False, 0, 0),
    ("NOT VULNERABLE", 0, True, 0, 0),
    ("VULNERABLE", 0, False, 1, 0),
    ("I cannot tell.", 1, False, 0, 1),
    ("I cannot tell.", 0, True, 0, 1),
])
def test_js_assertion(output, label, passed, flagged, unparsed):
    r = js_assert(output, {"label": label, "case_id": "x"})
    assert r["pass"] is passed and r["score"] == (1 if passed else 0)
    assert r["namedScores"] == {"flagged": flagged, "unparsed": unparsed}


@needs_node
def test_js_assertion_requires_label():
    assert "label" in js_assert("VULNERABLE", {"case_id": "x"})["thrown"]


# ---------- converter ----------

def _row(case_id, output, flagged, failure=0, label="qwen2.5-coder:7b"):
    return {"vars": {"case_id": case_id, "label": 1}, "response": {"output": output}, "failureReason": failure,
            "namedScores": {"flagged": flagged}, "provider": {"id": "ollama:completion:x", "label": label}}


def test_converter_rows_and_errors(tmp_path):
    doc = {"results": {"results": [
        _row("V01-v-clean-none", "VULNERABLE\nSQLi", 1),
        _row("V01-f-clean-none", "SAFE", 0, failure=0),
        _row("V02-f-clean-none", "VULNERABLE", 1, failure=1),
        _row("V03-f-clean-none", "hmm", 0, failure=0),
        {"vars": {"case_id": "V04-v-clean-none"}, "response": {"error": "boom"}, "failureReason": 2},
    ]}}
    src, dst = tmp_path / "r.json", tmp_path / "p.csv"
    src.write_text(json.dumps(doc))
    rows, errors = to_predictions_csv.main(str(src), str(dst))
    assert errors == 1
    assert [(r["case_id"], r["flagged"], r["parse_mode"]) for r in rows] == [
        ("V01-v-clean-none", "true", "first_line"), ("V01-f-clean-none", "false", "first_line"),
        ("V02-f-clean-none", "true", "first_line"), ("V03-f-clean-none", "false", "unparsed")]
    import csv
    back = list(csv.DictReader(open(dst)))
    assert back[0]["model"] == "qwen2.5-coder:7b" and back[0]["response"] == "VULNERABLE\nSQLi"


def test_converter_detects_parser_disagreement():
    with pytest.raises(ValueError, match="verdict.js says"):
        to_predictions_csv.convert({"results": {"results": [_row("V01-v-clean-none", "SAFE", 1)]}})


def test_converter_output_is_accepted_by_score_predictions(tmp_path):
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import score_predictions
    doc = {"results": {"results": [_row(c["case_id"], "VULNERABLE" if c["label"] else "SAFE", c["label"])
                                   for c in CASES if c["condition"] == "clean"]}}
    rows, _ = to_predictions_csv.convert(doc)
    dst = tmp_path / "p.csv"
    import csv
    with open(dst, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=to_predictions_csv.FIELDS)
        w.writeheader()
        w.writerows(rows)
    assert all(score_predictions.to_bool(r["flagged"]) == bool(c["label"])
               for r, c in zip(csv.DictReader(open(dst)), [c for c in CASES if c["condition"] == "clean"]))


# ---------- optional: real promptfoo, echo provider (no model) ----------

@pytest.mark.skipif(not os.environ.get("PROMPTFOO_BIN"), reason="set PROMPTFOO_BIN to run promptfoo itself")
def test_promptfoo_echo_renders_exact_prompts(tmp_path):
    env = dict(os.environ, PROMPTFOO_DISABLE_TELEMETRY="1", PROMPTFOO_DISABLE_UPDATE="1",
               PROMPTFOO_CONFIG_DIR=str(tmp_path / "home"), PROMPTFOO_CACHE_PATH=str(tmp_path / "home" / "cache"))
    out = tmp_path / "echo.json"
    proc = subprocess.run([os.environ["PROMPTFOO_BIN"], "eval", "-c", "promptfooconfig.yaml", "-r", "echo", "--no-cache",
                    "--no-write", "--no-share", "--no-table", "--no-progress-bar", "-o", str(out)],
                   cwd=EXAMPLE, env=env, capture_output=True, text=True)
    # promptfoo exits 100 when some assertions fail (expected with echo: half the twins are "wrong")
    assert proc.returncode in (0, 100), proc.stderr[-2000:]
    rows = to_predictions_csv.result_rows(json.load(open(out)))
    by_id = {c["case_id"]: c for c in CASES}
    assert len(rows) == 840
    assert all(r["response"]["output"] == REVIEW_PROMPT.format(code=by_id[r["vars"]["case_id"]]["code"]) for r in rows)
    preds, errors = to_predictions_csv.convert(json.load(open(out)))
    assert errors == 0 and len(preds) == 840
