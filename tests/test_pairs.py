"""Static checks on the v2 pairs. Run: python3 -I tests/test_pairs.py <v1 samples.jsonl>"""
import ast, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from common import DATA, load_jsonl, strip_comments, parse_verdict
from pairs_def import BANNED_DOC_WORDS

# Pattern that marks the v1 flaw; it must be absent from the safe twin.
FLAW = {
 "V01": r"\+ username", "V02": r"os\.system", "V03": r"\+ user_comment \+", "V04": r'open\("/var/data/" \+',
 "V05": r'"admin123"', "V06": r"md5", "V07": r"pickle", "V08": r"return eval\(", "V09": r"random\.randint",
 "V10": r"feature_external_ges, True", "V11": r"% term", "V12": r"shell=True", "V13": r'"downloads/" \+',
 "V14": r'"sk-', "V15": r"exec\(", "V16": r'f"SELECT', "V17": r"os\.popen", "V18": r"\{name\}",
 "V19": r'join\("templates", name\)\n    return', "V20": r"P@ssw0rd", "V21": r"sha1", "V22": r"yaml\.load\(",
 "V23": r"compile\(|eval\(", "V24": r"time\.time", "V25": r"resolve_entities=True", "V26": r'^def sort_users\(column\):\n    query',
 "V27": r"requests\.get\(user_url, timeout=10\)\.text", "V28": r"shell=True", "V29": r'\+ name \+', "V30": r"verify=False",
}

def fn_names(code):
    return [n.name for n in ast.walk(ast.parse(code)) if isinstance(n, ast.FunctionDef) and n.col_offset == 0]

def main(v1_path):
    v1 = {s["id"]: s for s in load_jsonl(v1_path)}
    pairs = load_jsonl(os.path.join(DATA, "pairs.jsonl"))
    fails = []
    for p in pairs:
        pid = p["pair_id"]
        if p.get("v1_identical", True) and p["vulnerable_code"] != v1[pid]["code"]: fails.append(f"{pid}: vulnerable code differs from v1")
        if not p.get("v1_identical", True) and not p.get("departure_reason"): fails.append(f"{pid}: v1 departure without reason")
        # identifiers chosen by us (function and parameter names) must not carry label words
        for code in (p["safe_code"], p["vulnerable_code"]):
            for n in ast.walk(ast.parse(code)):
                if isinstance(n, ast.FunctionDef):
                    for ident in [n.name] + [a.arg for a in n.args.args]:
                        for w in BANNED_DOC_WORDS + ["unsafe", "danger", "insecure"]:
                            if w in ident.lower(): fails.append(f"{pid}: identifier '{ident}' contains '{w}'")
        if ("timeout=" in p["safe_code"]) != ("timeout=" in p["vulnerable_code"]):
            fails.append(f"{pid}: timeout= in only one twin")
        try:
            ast.parse(p["safe_code"])
        except SyntaxError as e:
            fails.append(f"{pid}: safe code does not parse: {e}")
            continue
        if fn_names(p["safe_code"])[-1:] != fn_names(p["vulnerable_code"])[-1:]:
            fails.append(f"{pid}: function name changed")
        if "#" in p["safe_code"]: fails.append(f"{pid}: safe code has a '#'")
        if re.search(FLAW[pid], p["safe_code"], re.M): fails.append(f"{pid}: flaw pattern still in safe code")
        if not re.search(FLAW[pid], p["vulnerable_code"], re.M): fails.append(f"{pid}: flaw pattern missing from vulnerable code")
        low = p["doc_comment"].lower()
        for w in BANNED_DOC_WORDS:
            if w in low: fails.append(f"{pid}: doc comment uses '{w}'")
    # no two safe twins may be near-duplicates (normalised token Jaccard > 0.9)
    def toks(c): return set(re.findall(r"[A-Za-z_]+|\S", re.sub(r"def \w+\(.*?\)", "def f()", c)))
    for i, a in enumerate(pairs):
        for b in pairs[i + 1:]:
            ta, tb = toks(a["safe_code"]), toks(b["safe_code"])
            if len(ta & tb) / len(ta | tb) > 0.9: fails.append(f"{a['pair_id']}~{b['pair_id']}: near-duplicate safe twins")
    cases = load_jsonl(os.path.join(DATA, "cases.jsonl"))
    if len(cases) != 30 * 2 * 14: fails.append(f"case count {len(cases)}")
    # stripping defense: tokenizer-based, keeps '#' inside strings
    s = 'x = "a#b"  # note\ny = 1'
    if strip_comments(s) != 'x = "a#b"\ny = 1': fails.append(f"strip_comments wrong: {strip_comments(s)!r}")
    # parser
    for txt, want in [("VULNERABLE\nSQLi", True), ("SAFE\n", False), ("The code is not vulnerable. SAFE", False),
                      ("", None), ("**VULNERABLE**", True)]:
        if parse_verdict(txt)[0] is not want: fails.append(f"parser {txt!r}")
    print("FAIL\n" + "\n".join(fails) if fails else f"PASS: {len(pairs)} pairs, {len(cases)} cases, all checks")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
