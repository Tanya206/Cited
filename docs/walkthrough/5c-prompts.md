# Walkthrough: 5C, the prompt as versioned configuration

Branch `ws/5c-prompts`, 2026-11-18. Decision record: `docs/decisions/001-prompts-as-versioned-config.md`.

## The problem in one sentence

If the prompt can change without anyone noticing, a faithfulness score from last week and one
from today might come from different prompts, and you could not tell.

## 1. Look at the prompt as a file

```powershell
Get-Content prompts\answer_v1.yaml
```

Things to notice:
- `version: answer_v1` must equal the file name. The loader refuses a mismatch.
- `${question}`, `${evidence}`, `${refusal}` are placeholders. Python's `string.Template` is
  used instead of `str.format` because the prompt contains literal JSON braces
  (`{"answer": ...}`) and evidence text may contain `$` or `{}`.
- The evidence format (how each chunk is labelled, the separator, the 24,000-character
  budget) is part of the prompt too, so it is versioned with it.

## 2. Load it and see what gets recorded

```powershell
.\venv\Scripts\python.exe -c "from app.core.prompts import load_prompt; p = load_prompt(); print(p.version, p.sha256[:12]); print(p.refusal)"
```

The hash is how you can prove later that `answer_v1` was never edited after results were
produced with it.

## 3. Proof that nothing changed for the model

Before moving the text, the exact prompts the old code sent were captured into
`tests/fixtures/answer_v1_answer.txt` and `answer_v1_repair.txt`. The new code must produce
the same bytes:

```powershell
.\venv\Scripts\python.exe -m pytest -q tests/test_prompts.py -v
```

Try the mutation yourself: change one word in `prompts/answer_v1.yaml`, run the command
again, and see two tests fail. Then undo the change:

```powershell
git checkout -- prompts/answer_v1.yaml
```

That failure is the point: a changed prompt must be saved as `answer_v2.yaml`.

## 4. Where the version shows up

| Place | Field |
|---|---|
| `/answer` response | `prompt_version`, `prompt_sha256` (`null` when validation rejected the question and no prompt was sent) |
| Langfuse trace | metadata and output: `prompt_version`, `prompt_sha256` |
| `eval/answer_runs.jsonl` | per item: `prompt_version`, `prompt_sha256` |
| `eval/ragas_results.json` | per row: `id`, `prompt_version`, `prompt_sha256` |

Old answer runs (3 Nov) have no version. They are left as `null`, not relabelled: the text was
the same, but the file does not record it, and we only claim what is recorded.

The retrieval evaluation does not use the prompt, so it does not record a prompt version.

## 5. Interview framing

"I treat the prompt like a database migration: versions are immutable, a change is a new
version, and every result records the version and a content hash. A test pins the hash, so
an accidental edit fails CI. I chose a YAML file in git over a hosted prompt registry because
there is one prompt, one team, and I did not want a network call or a second source of truth
on the request path."

## Numbers

| | Before | After |
|---|---|---|
| Tests | 34 passed | 46 passed |
| Rendered prompt vs old code | n/a | byte-identical (answer and repair) |
| Retrieval baseline | unchanged | unchanged (no index rebuilt) |
