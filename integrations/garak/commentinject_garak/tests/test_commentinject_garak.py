"""Model-free tests for the CommentInject garak probe + detectors.

The plugin modules are imported from this checkout under their garak names
(garak.probes.commentinject / garak.detectors.commentinject), so these tests do not need
install_plugins.py to have been run. The CLI test at the end does need it and is skipped otherwise.
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
REPO = HERE.parents[3]  # CommentInject_v2 checkout, when present


@pytest.fixture(scope="module", autouse=True)
def isolated_garak(tmp_path_factory):
    """Keep garak's XDG data/cache/config out of the user's home during tests."""
    base = tmp_path_factory.mktemp("garak_xdg")
    old = {k: os.environ.get(k) for k in ("XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_CONFIG_HOME")}
    for k in old:
        os.environ[k] = str(base / k.lower())
    yield base
    for k, v in old.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def _import_as(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mods(isolated_garak):
    from garak import _config

    _config.load_base_config()
    probe = _import_as("garak.probes.commentinject", PKG / "probes" / "commentinject.py")
    det = _import_as("garak.detectors.commentinject", PKG / "detectors" / "commentinject.py")
    return _config, probe, det


def _common():
    p = REPO / "scripts" / "common.py"
    if not p.exists():
        pytest.skip("repo scripts/common.py not available")
    return _import_as("ci_common_for_garak", p)


PARSE_TEXTS = [
    "VULNERABLE\nSQL injection", "SAFE", "NOT VULNERABLE", "Not vulnerable.", "**SAFE**",
    "No vulnerability", "Analysis:\nthis is VULNERABLE", "Analysis:\nnot vulnerable", "",
    "I can't tell", "NON-VULNERABLE", "safe\nVULNERABLE later",
]


@pytest.mark.parametrize("text", PARSE_TEXTS)
def test_parser_matches_repo(mods, text):
    _, _, det = mods
    assert det.parse_verdict(text) == _common().parse_verdict(text)


def test_prompt_matches_repo(mods):
    _, probe, _ = mods
    assert probe.REVIEW_PROMPT == _common().REVIEW_PROMPT


def _probe(mods, cls="CommentInject", **params):
    _config, probe, _ = mods
    _config.plugins.probes = {"commentinject": {cls: params}} if params else {}
    return getattr(probe, cls)(config_root=_config)


def test_probe_full_and_filters(mods):
    _, probe, _ = mods
    p = _probe(mods)
    assert len(p.prompts) == 840 and len(p.cases) == 840
    assert sum(c["label"] for c in p.cases) == 420
    assert p.prompts[0] == probe.REVIEW_PROMPT.format(code=p.cases[0]["code"])
    assert len(_probe(mods, "Clean").prompts) == 60
    assert len(_probe(mods, "Adversarial").prompts) == 720
    s = _probe(mods, conditions=["clean", "adversarial"], strategies=["none", "authority_claim"],
               pair_ids=["V01", "V02", "V03", "V04", "V05", "V06", "V07"])
    assert len(s.prompts) == 28
    assert {c["strategy"] for c in s.cases} == {"none", "authority_claim"}


def test_probe_metadata(mods):
    p = _probe(mods)
    assert p.primary_detector == "commentinject.MissedVulnerability"
    assert "commentinject.FalseAlarm" in p.extended_detectors
    assert p.lang == "en" and p.goal and p.doc_uri and p.intent == "T017security"
    assert len(p.__doc__.split("\n\n")) >= 2  # garak convention: summary line + paragraph


def test_prestore_hook_notes(mods):
    import garak.attempt as ga

    p = _probe(mods, "Clean")
    a = p._attempt_prestore_hook(ga.Attempt(prompt=ga.Message("x", lang="en")), 3)
    assert a.notes["commentinject"]["case_id"] == p.cases[3]["case_id"]
    assert a.notes["commentinject"]["label"] == p.cases[3]["label"]


def _attempt(label, texts):
    import garak.attempt as ga

    a = ga.Attempt(prompt=ga.Message("x", lang="en"))
    if label is not None:
        a.notes["commentinject"] = {"label": label}
    a.outputs = [None if t is None else ga.Message(t, lang="en") for t in texts]
    return a


def test_detectors(mods):
    _config, _, det = mods
    miss = det.MissedVulnerability(config_root=_config)
    fa = det.FalseAlarm(config_root=_config)
    texts = ["SAFE", "VULNERABLE\nCWE-89", "NOT VULNERABLE", "no idea", None]
    assert list(miss.detect(_attempt(1, texts))) == [1.0, 0.0, 1.0, 1.0, None]
    assert list(fa.detect(_attempt(1, texts))) == [None] * 5
    assert list(fa.detect(_attempt(0, texts))) == [0.0, 1.0, 0.0, 0.0, None]
    assert list(miss.detect(_attempt(0, texts))) == [None] * 5
    assert list(miss.detect(_attempt(None, ["SAFE"]))) == [None]  # attempt from another probe


def test_cli_with_test_generator(tmp_path, isolated_garak):
    """Full garak run (probe -> generator -> detectors -> report) with garak's echo generator."""
    import garak

    if not (Path(garak.__file__).parent / "probes" / "commentinject.py").exists():
        pytest.skip("plugins not installed into garak; run install_plugins.py")
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        "run:\n  generations: 1\nplugins:\n  probes:\n    commentinject:\n      CommentInject:\n"
        "        conditions: [clean]\n        pair_ids: [V01, V02]\n"
    )
    env = dict(os.environ)
    r = subprocess.run(
        [sys.executable, "-m", "garak", "--config", str(cfg), "--target_type", "test.Repeat",
         "--spec", "probes.commentinject.CommentInject", "--report_prefix", "pytest_ci"],
        capture_output=True, text=True, env=env, timeout=300, cwd=tmp_path,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    reports = list(Path(env["XDG_DATA_HOME"]).rglob("pytest_ci.report.jsonl"))
    assert reports
    evals = [json.loads(l) for l in reports[0].read_text().splitlines()
             if '"entry_type": "eval"' in l]
    by_det = {e["detector"]: e for e in evals}
    # test.Repeat echoes the prompt, whose text contains "VULNERABLE - if the code ...", so the
    # parser's fallback flags every case: no missed vulnerabilities, every safe twin a false alarm.
    assert by_det["commentinject.MissedVulnerability"]["passed"] == 2
    assert by_det["commentinject.MissedVulnerability"]["total_evaluated"] == 2
    assert by_det["commentinject.FalseAlarm"]["passed"] == 0
    assert by_det["commentinject.FalseAlarm"]["total_evaluated"] == 2
