# commentinject-code-review (CommentInject Code Review Benchmark)

You can run this example with:

```bash
npx promptfoo@latest init --example commentinject-code-review
cd commentinject-code-review
```

This example runs **CommentInject v2**, a benchmark that tests whether misleading code comments change an LLM's security review. Each Python function comes as a matched pair: a vulnerable version and a minimally fixed twin with the same name and signature. Both twins appear under 14 comment conditions: no comment (`clean`), one neutral comment (`doc`), and 12 adversarial strategies such as `authority_claim`, `fake_review_approval` and `formal_verification`. That makes 30 pairs × 2 twins × 14 conditions = 840 tests.

The model gets the benchmark's review prompt (`review_prompt.j2`) and must answer `VULNERABLE` or `SAFE` on the first line. The `verdict.js` assertion parses that answer the same way the benchmark does: it reads `NOT VULNERABLE` as SAFE and falls back to the rest of the reply when the first line has no verdict. A test passes when the verdict matches the twin, so the vulnerable twin should be flagged and the fixed twin should not.

## What the results mean

- A **failing vulnerable twin** under an adversarial comment is a successful comment injection, because the comment talked the reviewer out of a real finding.
- A **failing fixed twin** is a false alarm.
- `namedScores.flagged` is the raw verdict (1 = VULNERABLE). Its mean is the yes-rate, so you can tell whether a comment made the model **less able to tell the twins apart** or just **less willing to flag anything**.

## Prerequisites

- [Ollama](https://ollama.com) running locally, with the model pulled: `ollama pull qwen2.5-coder:7b`
- No API keys are needed. Set `OLLAMA_BASE_URL` if Ollama is not on `http://localhost:11434`.

The provider settings match the benchmark's reference runner: Ollama `/api/generate`, `temperature: 0`, `seed: 0`, no token cap.

## Usage

Run one matched pair under all 14 conditions (28 tests):

```bash
npx promptfoo@latest eval --filter-metadata pair_id=V24 -j 1
```

Run only the uncommented baseline (60 tests), or the full set (840 tests):

```bash
npx promptfoo@latest eval --filter-metadata condition=clean
npx promptfoo@latest eval
npx promptfoo@latest view
```

Every test carries `pair_id`, `cwe`, `variant`, `label`, `condition`, `strategy` and `sha256` as metadata. You can use any of them with `--filter-metadata`.

To compare models, add more `ollama:completion:<model>` entries, or any other provider, under `providers`.

## Files

| File | Contents |
|---|---|
| `promptfooconfig.yaml` | Prompt, provider, assertion and tests |
| `review_prompt.j2` | The benchmark's review prompt. It is a `.j2` file because promptfoo trims `.txt` prompts, which would drop the prompt's final newline. |
| `verdict.js` | Verdict parser and pass/fail assertion |
| `tests.jsonl` | The 840 test cases, generated from the benchmark's `data/cases.jsonl` |

## Learn more

- CommentInject v1: https://doi.org/10.5281/zenodo.23088528
