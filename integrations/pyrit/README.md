# CommentInject v2 for PyRIT

`commentinject_dataset.py` is a [PyRIT](https://github.com/microsoft/PyRIT) seed-dataset loader. It is written to drop into `pyrit/datasets/seed_datasets/remote/` and follows the current public-dataset loaders there, notably `cyberseceval_prompt_injection_dataset.py`:

- `_CommentInjectDataset(_RemoteDatasetLoader)` implements `_fetch_dataset_async(*, cache=True) -> SeedDataset` and the `dataset_name` property (`"commentinject"`). It inherits the final `fetch_dataset_async`, which sets `SeedOrigin.REMOTE`.
- It has `source` and `source_type: Literal["public_url", "file"]` and loads through `_fetch_from_url`, so local files, URLs and PyRIT's cache all work.
- It sets the class metadata `harm_categories = []`, `modalities = (Modality.TEXT,)`, `size = "large"` and `tags`.
- Its enum filters are `CommentInjectCondition`, `CommentInjectStrategy` and `CommentInjectVariant`, plus `pair_ids`. They are checked with `_validate_enums`, and an empty list raises `ValueError`.
- It checks the schema of every row (keys, types, enums, label vs. variant, condition vs. strategy, duplicate ids, `sha256` of the code, and 840 rows when unfiltered). An empty result raises `ValueError`.
- Each case becomes one `user` `SeedPrompt` with its own `prompt_group_id`. Its value is the benchmark's review prompt with the code filled in. Pass `include_review_prompt=False` to get the bare code. The metadata holds `case_id`, `pair_id`, `cwe`, `variant`, `label`, `condition`, `strategy`, `sha256`, `expected_verdict` and `twin_key`. `twin_key` is shared by the two twins under the same comment.
- `parse_commentinject_verdict()` is a copy of `scripts/common.py:parse_verdict`, for scoring replies.

Importing the module registers the loader with `SeedDatasetProvider`, as for the built-in loaders.

## Use

```python
import asyncio
from commentinject_dataset import _CommentInjectDataset, CommentInjectCondition, parse_commentinject_verdict

ds = asyncio.run(_CommentInjectDataset(source="data/cases.jsonl", source_type="file",
                                       conditions=[CommentInjectCondition.CLEAN]).fetch_dataset_async(cache=False))
print(len(ds.seeds), ds.seeds[0].metadata)
```

The default `source` is a placeholder on a `.invalid` host, so a default fetch fails at once. The public v2 release is not out yet. Pin the real URL (a commit or a Zenodo record) on release.

## Test

```bash
SP=<tmp>/-Users-sc-Documents-RP/9ee54619-9b20-46fc-9b5e-c5342c2043f2/scratchpad
/usr/local/bin/python3.14 -m venv $SP/venv_pyrit
$SP/venv_pyrit/bin/pip install pyrit pytest pytest-asyncio
# HOME is redirected because `import pyrit` creates its dbdata folder under ~/Library/Application Support
HOME=$SP/pyrit_home $SP/venv_pyrit/bin/python -I -B -m pytest -q -p no:cacheprovider integrations/pyrit/tests
# plus the 5-request smoke pass through OpenAIChatTarget -> Ollama's OpenAI-compatible /v1 endpoint
HOME=$SP/pyrit_home COMMENTINJECT_OLLAMA_SMOKE=1 $SP/venv_pyrit/bin/python -I -B -m pytest -q -p no:cacheprovider -s integrations/pyrit/tests -k smoke
```

The smoke test uses `OpenAIChatTarget(endpoint="http://localhost:11434/v1", model_name="qwen2.5-coder:7b", auth_mode="none", temperature=0, seed=0)`, so no key is used. It runs with PyRIT's `IN_MEMORY` memory and `load_defaults=False`, `env_files=[]`. It compares each verdict with the stored `scripts/run.py` verdict in `results/phase2/raw_seed0_rc2.jsonl`.

Tested versions and results are in `integrations/LOCAL_TEST_LOG.md`.

## Toward an upstream PR (not done)

- Open an issue first, as PyRIT's contributing guide asks, and sign Microsoft's CLA.
- The file needs the repo's MIT header (`# Copyright (c) Microsoft Corporation.`). It is left out here on purpose.
- Add the two `TYPE_CHECKING` and lazy-export entries in `pyrit/datasets/seed_datasets/remote/__init__.py`. Add a bib entry for the `[@...]` reference style. Add a row to the datasets doc page.
- Port `tests/` to upstream's style in `tests/unit/datasets/test_<name>_dataset.py`, using mocked `_fetch_from_url` rows rather than the real file. Upstream may also want an integration test that fetches the pinned URL.
- Run upstream `ruff`, `mypy` and pre-commit. They were not run here.
- Pin `DATASET_URL` to the public release.
