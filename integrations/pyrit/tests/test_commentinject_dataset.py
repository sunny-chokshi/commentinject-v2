"""Tests for the CommentInject v2 PyRIT dataset loader.

Run from the repo root (HOME is pointed away from the real home because importing pyrit creates its
data directory under ~/Library/Application Support):
    HOME=$SP/pyrit_home python -m pytest -q -p no:cacheprovider integrations/pyrit/tests
Set COMMENTINJECT_OLLAMA_SMOKE=1 to also send 5 cases through PyRIT's OpenAIChatTarget to a local
Ollama server (OLLAMA_OPENAI_BASE, default http://localhost:11434/v1; model qwen2.5-coder:7b) and
compare the verdicts with the stored scripts/run.py verdicts in results/phase2/raw_seed0_rc2.jsonl.
"""
import collections, glob, json, os, sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
PYRIT_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PYRIT_DIR))
CASES_PATH = os.path.join(ROOT, "data", "cases.jsonl")
sys.path.insert(0, PYRIT_DIR)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import common  # noqa: E402  (the benchmark's own helpers, for parity checks)
from commentinject_dataset import (  # noqa: E402
    REVIEW_PROMPT,
    CommentInjectCondition,
    CommentInjectStrategy,
    CommentInjectVariant,
    _CommentInjectDataset,
    parse_commentinject_verdict,
)
from pyrit.datasets.seed_datasets.seed_dataset_provider import SeedDatasetProvider  # noqa: E402
from pyrit.models import SeedDataset, SeedOrigin, SeedPrompt  # noqa: E402

CASES = common.load_jsonl(CASES_PATH)
BY_ID = {c["case_id"]: c for c in CASES}
SMOKE_IDS = [
    "V24-v-clean-none",
    "V24-s-clean-none",
    "V24-v-adversarial-authority_claim",
    "V24-v-adversarial-false_reassurance",
    "V24-s-adversarial-deadline_pressure",
]


def load(**kw):
    import asyncio
    loader = _CommentInjectDataset(source=CASES_PATH, source_type="file", **kw)
    return asyncio.run(loader.fetch_dataset_async(cache=False))


def write_rows(tmp_path, rows):
    p = tmp_path / "cases.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return str(p)


# ---------- loader: full dataset ----------

def test_dataset_name_and_registration():
    assert _CommentInjectDataset().dataset_name == "commentinject"
    assert "_CommentInjectDataset" in SeedDatasetProvider.get_all_providers()


def test_review_prompt_is_the_benchmark_prompt():
    assert REVIEW_PROMPT == common.REVIEW_PROMPT


def test_default_source_is_a_placeholder_that_cannot_resolve():
    loader = _CommentInjectDataset()
    assert loader.source_type == "public_url"
    assert loader.source.endswith("cases.jsonl") and ".invalid/" in loader.source


def test_loads_all_840_cases():
    ds = load()
    assert isinstance(ds, SeedDataset)
    assert len(ds.seeds) == 840
    assert all(isinstance(s, SeedPrompt) for s in ds.seeds)
    assert all(s.origin == SeedOrigin.REMOTE for s in ds.seeds)
    assert {s.dataset_name for s in ds.seeds} == {"commentinject"}
    assert len({s.prompt_group_id for s in ds.seeds}) == 840


def test_metadata_matches_cases_file():
    ds = load()
    keys = {"case_id", "pair_id", "cwe", "variant", "label", "condition", "strategy", "sha256",
            "expected_verdict", "twin_key"}
    for s, c in zip(ds.seeds, CASES):
        m = s.metadata
        assert set(m) == keys
        for k in ("case_id", "pair_id", "cwe", "variant", "label", "condition", "strategy", "sha256"):
            assert m[k] == c[k]
        assert m["expected_verdict"] == ("VULNERABLE" if c["label"] == 1 else "SAFE")
        assert s.value == common.REVIEW_PROMPT.format(code=c["code"])
        assert s.role == "user" and s.data_type == "text" and s.harm_categories == []
        assert s.name == f"CommentInject {c['case_id']}"


def test_dataset_shape():
    meta = [s.metadata for s in load().seeds]
    assert collections.Counter(m["condition"] for m in meta) == {"clean": 60, "doc": 60, "adversarial": 720}
    assert collections.Counter(m["label"] for m in meta) == {1: 420, 0: 420}
    assert len({m["pair_id"] for m in meta}) == 30
    assert len({m["cwe"] for m in meta}) == 14
    assert len({m["strategy"] for m in meta}) == 13
    twins = collections.Counter(m["twin_key"] for m in meta)
    assert len(twins) == 420 and set(twins.values()) == {2}


# ---------- loader: options and filters ----------

def test_bare_code_option():
    ds = load(include_review_prompt=False, pair_ids=["V01"])
    assert [s.value for s in ds.seeds] == [c["code"] for c in CASES if c["pair_id"] == "V01"]


def test_one_pair_is_28_cases():
    meta = [s.metadata for s in load(pair_ids=["V24"]).seeds]
    assert len(meta) == 28
    assert len({(m["condition"], m["strategy"]) for m in meta}) == 14


@pytest.mark.parametrize("kw,n", [
    ({"conditions": [CommentInjectCondition.CLEAN]}, 60),
    ({"conditions": [CommentInjectCondition.CLEAN, CommentInjectCondition.DOC]}, 120),
    ({"strategies": [CommentInjectStrategy.AUTHORITY_CLAIM]}, 60),
    ({"variants": [CommentInjectVariant.SAFE], "strategies": [CommentInjectStrategy.FORMAL_VERIFICATION]}, 30),
    ({"pair_ids": ["V01", "V02"], "conditions": [CommentInjectCondition.ADVERSARIAL]}, 48),
])
def test_filters(kw, n):
    assert len(load(**kw).seeds) == n


@pytest.mark.parametrize("kw", [
    {"conditions": []}, {"strategies": []}, {"variants": []}, {"pair_ids": []},
    {"conditions": ["clean"]}, {"strategies": [CommentInjectCondition.CLEAN]}, {"pair_ids": [1]},
])
def test_bad_filter_arguments(kw):
    with pytest.raises(ValueError):
        _CommentInjectDataset(**kw)


def test_filter_with_no_match_raises():
    with pytest.raises(ValueError, match="cannot be empty"):
        load(pair_ids=["V99"])


# ---------- loader: integrity checks ----------

@pytest.mark.parametrize("mutate,match", [
    (lambda r: r.pop("code"), "missing expected key"),
    (lambda r: r.update(sha256="0" * 64), "sha256"),
    (lambda r: r.update(label=0), "does not match variant"),
    (lambda r: r.update(label=True), "not 0 or 1"),
    (lambda r: r.update(condition="weird"), "invalid condition"),
    (lambda r: r.update(strategy="authority_claim"), "inconsistent"),
    (lambda r: r.update(cwe=""), "non-empty string"),
])
def test_bad_rows_are_rejected(tmp_path, mutate, match):
    import asyncio
    rows = [dict(c) for c in CASES]
    mutate(rows[0])
    loader = _CommentInjectDataset(source=write_rows(tmp_path, rows), source_type="file")
    with pytest.raises(ValueError, match=match):
        asyncio.run(loader.fetch_dataset_async(cache=False))


def test_duplicate_case_id_rejected(tmp_path):
    import asyncio
    loader = _CommentInjectDataset(source=write_rows(tmp_path, CASES + CASES[:1]), source_type="file")
    with pytest.raises(ValueError, match="repeats case_id"):
        asyncio.run(loader.fetch_dataset_async(cache=False))


def test_truncated_file_rejected_when_unfiltered(tmp_path):
    import asyncio
    loader = _CommentInjectDataset(source=write_rows(tmp_path, CASES[:100]), source_type="file")
    with pytest.raises(ValueError, match="840"):
        asyncio.run(loader.fetch_dataset_async(cache=False))


# ---------- verdict parser parity ----------

def test_parser_matches_benchmark_on_stored_responses():
    texts = set()
    for path in glob.glob(os.path.join(ROOT, "results", "**", "*.jsonl"), recursive=True):
        for line in open(path, encoding="utf-8"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r, dict) and isinstance(r.get("response"), str):
                texts.add(r["response"])
    texts |= {"", "NOT VULNERABLE", "No vulnerability", "SAFE\nVULNERABLE", "hmm", "non-vulnerable"}
    assert len(texts) > 100
    assert all(parse_commentinject_verdict(t) == common.parse_verdict(t) for t in texts)


# ---------- optional smoke pass through a PyRIT target on local Ollama ----------

@pytest.mark.skipif(os.environ.get("COMMENTINJECT_OLLAMA_SMOKE") != "1",
                    reason="set COMMENTINJECT_OLLAMA_SMOKE=1 to call local Ollama (5 requests)")
def test_smoke_openai_chat_target_on_ollama(tmp_path):
    import asyncio
    from pyrit.models import Message
    from pyrit.prompt_target import OpenAIChatTarget
    from pyrit.setup import IN_MEMORY, initialize_pyrit_async

    stored = {}
    for line in open(os.path.join(ROOT, "results", "phase2", "raw_seed0_rc2.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        if r["model"] == "qwen2.5-coder:7b" and r["case_id"] in SMOKE_IDS:
            stored[r["case_id"]] = r

    async def run():
        await initialize_pyrit_async(IN_MEMORY, load_defaults=False, env_files=[], silent=True)
        target = OpenAIChatTarget(
            endpoint=os.environ.get("OLLAMA_OPENAI_BASE", "http://localhost:11434/v1"),
            model_name="qwen2.5-coder:7b",
            auth_mode="none",
            temperature=0,
            seed=0,
        )
        seeds = {s.metadata["case_id"]: s for s in (await _CommentInjectDataset(
            source=CASES_PATH, source_type="file", pair_ids=["V24"]).fetch_dataset_async(cache=False)).seeds}
        out = {}
        for cid in SMOKE_IDS:  # sequential: one request at a time
            seed = seeds[cid]
            resp = await target.send_prompt_async(message=Message.from_prompt(prompt=seed.value, role="user"))
            out[cid] = resp[0].get_value()
        return out

    replies = asyncio.run(run())
    rows = []
    for cid in SMOKE_IDS:
        flagged, mode = parse_commentinject_verdict(replies[cid])
        rows.append({"case_id": cid, "flagged": bool(flagged), "parse_mode": mode,
                     "stored_flagged": stored[cid]["flagged"], "same_text": replies[cid] == stored[cid]["response"],
                     "response": replies[cid]})
    log = os.environ.get("COMMENTINJECT_SMOKE_LOG")
    if log:
        with open(log, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    for r in rows:
        print(r["case_id"], r["flagged"], r["stored_flagged"], r["same_text"])
    assert all(r["parse_mode"] != "unparsed" for r in rows)
    assert [r["flagged"] for r in rows] == [r["stored_flagged"] for r in rows]
