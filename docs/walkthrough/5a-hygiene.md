# Walkthrough: 5A, hygiene and a CI that can pass

Branch `ws/5a-hygiene`, 2026-11-18. Read this top to bottom, running each command and
looking at its real output. Every number here came from a command run on this branch.

## 1. Why CI had never passed

Every GitHub Actions run since September failed at `pip install -r requirements.txt`.
The cause, reproduced locally without GitHub:

```powershell
.\venv\Scripts\python.exe -m pip install --dry-run --ignore-installed --only-binary=:all: --platform manylinux2014_x86_64 --python-version 3.11 --implementation cp --target $env:TEMP\t311 -r requirements.txt
```

On the old file this ends with `No matching distribution found for numpy==2.5.2`: numpy 2.5
publishes no wheels for Python 3.11, and CI ran 3.11 while the lock was taken from your 3.14
venv. Lesson: **the Python version is part of the lock**. Local and CI must use the same one.

The old `requirements.txt` was also not really a lock. Compared with the working venv it had
39 different versions, 41 missing packages, and version ranges for 5 direct dependencies. It
never declared PyStemmer, which `app/core/bm25_index.py:12` imports, so a clean install would
have failed at import even on the right Python.

**What changed:** `requirements.txt` is now `pip freeze` of the tested venv, minus the
packages the code never imports (`groq`, `pdfplumber` and their own dependencies). CI runs
Python 3.14, installs the CPU-only torch wheel, and runs `pip check`.

`pip check` found two real conflicts in your venv: Pillow 13.0.0 and pyarrow 26.0.0, while
Streamlit 1.65 requires Pillow <13 and pyarrow <26. The tests never imported Streamlit, so
nothing failed. Both are now pinned to the newest compatible versions (12.3.0 and 25.0.1).

See it yourself:

```powershell
.\venv\Scripts\python.exe -m pip check
```

```powershell
Get-Content requirements.in
```

One thing is not proven until CI runs: scikit-network 0.33.5 (a ragas dependency) has no
prebuilt Linux wheel for 3.14, so CI compiles it from source. If that step fails, the fallback
is Python 3.13 everywhere (it has wheels). This is logged in `docs/GAPS.md`.

## 2. The golden check without the corpus

The papers are copyrighted and gitignored, so CI has no `data/`. The validator now has two
modes:

```powershell
.\venv\Scripts\python.exe -m eval.validate_golden
```

```powershell
.\venv\Scripts\python.exe -m eval.validate_golden --structure-only
```

The first checks quotes against the real index (local only). The second checks the file
itself: unique IDs, refusal fields, evidence pages inside the expected pages, non-empty
quotes. CI runs the second.

## 3. H2: model output was rendered as HTML

`frontend/streamlit_app.py` put the model's answer inside HTML with
`unsafe_allow_html=True`. The answer is shaped by the user's question and by text in the
papers, so an answer containing `<img src=x onerror=...>` would run script in a visitor's
browser on the public demo. `frontend/render.py` now escapes it. The test
`tests/test_render.py` runs the real Streamlit script with that payload and checks it is
shown as text:

```powershell
.\venv\Scripts\python.exe -m pytest -q tests/test_render.py -v
```

Interview framing: "Treat LLM output as untrusted input. It is attacker-influenced through
the prompt and through retrieved documents (indirect prompt injection)."

## 4. M1: rate limits

Before, any provider error, including HTTP 429 (rate limit), triggered a second call without
JSON mode, and the API returned 502 "failed after a JSON retry". Measured on `main` with a
scripted 429: 2 calls and a misleading message. Now:

| Provider response | Calls | API status |
|---|---|---|
| 400 (JSON mode rejected) | 2 (retry without JSON mode) | normal answer |
| 429 (rate or daily limit) | 1 | 503 with the provider's `Retry-After` |
| other 5xx or network | 1 | 502 |

Why 503 and not 502: 502 says "the upstream gave a bad answer"; 503 says "temporarily
unavailable, come back after Retry-After". Clients and load balancers act differently on
each. That's an SRE point you can make from your Infosys experience.

```powershell
.\venv\Scripts\python.exe -m pytest -q tests/test_provider_errors.py -v
```

## 5. Tests for your extraction fixes

The two fixes from 2026-11-12 had no tests. The block filter and the header check are now
small functions (`remove_table_blocks`, `is_header_numeric` in `app/ingestion/extract.py`)
with tests for the 0.8 overlap rule, D4 (a suspicious table never removes body text) and the
numeric header. To prove the refactor changed nothing, all 44 papers were re-extracted into a
scratch folder: the JSON is identical to `data/extracted_structured`. A mutation check (put
the old "any table deletes text" line back) makes `test_suspicious_table_never_removes_body_text`
fail, so the test guards the real bug.

```powershell
.\venv\Scripts\python.exe -m pytest -q tests/test_extract.py -v
```

## 6. Smaller cleanup

Removed the 3 empty files (`Dockerfile` comes back properly in 5G), dead `extract_figures`,
unused `DEFAULT_MODEL` and `os` import. `scripts/audit_overlap.py` now imports the real
`overlap_fraction` instead of a private copy; it reports 30 partially overlapping blocks,
all of them kept in the body since the fix. Added the MIT licence and ignored the local skill
files.

## Numbers

| | Before (main) | After (this branch) |
|---|---|---|
| Tests | 18 passed | 34 passed |
| Clean checkout without `data/` | not tested | 34 passed; golden structure 0 errors |
| `pip check` | 2 conflicts | no broken requirements |
| Packages in the lock | 130 (with ranges) | 163 (all exact) |
| Retrieval baseline | unchanged: no index was rebuilt | unchanged |
