"""Convert Bandit JSON (`bandit -f json`) to the Semgrep-compatible JSON that RealVuln's default
parser reads (parsers/semgrep.py; the same shape as llm-bench/prompts/output-schema.json).

Usage: python3 -I integrations/realvuln/bandit_to_semgrep.py bandit.json results.json
"""
from __future__ import annotations

import json
import sys

SEVERITY = {"HIGH": "ERROR", "MEDIUM": "WARNING", "LOW": "INFO"}


def convert(bandit: dict) -> dict:
    results = []
    for r in bandit.get("results", []):
        path = r["filename"].replace("\\", "/")
        while path.startswith("./"):
            path = path[2:]
        cwe = (r.get("issue_cwe") or {}).get("id")
        line = r.get("line_number") or 1
        col = (r.get("col_offset") or 0) + 1
        end_col = r.get("end_col_offset")
        results.append({
            "check_id": f"bandit.{r['test_id']}.{r['test_name']}",
            "path": path,
            "start": {"line": line, "col": col},
            "end": {"line": (r.get("line_range") or [line])[-1],
                    "col": (end_col + 1) if isinstance(end_col, int) else col},
            "extra": {
                "message": r.get("issue_text", ""),
                "severity": SEVERITY.get(r.get("issue_severity", ""), "INFO"),
                "metadata": {"cwe": [f"CWE-{cwe}"] if cwe else [],
                             "confidence": r.get("issue_confidence", "").lower()},
            },
        })
    return {"version": "1.0.0", "results": results, "errors": bandit.get("errors", [])}


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        data = convert(json.load(f))
    with open(sys.argv[2], "w") as f:
        json.dump(data, f, indent=1)
