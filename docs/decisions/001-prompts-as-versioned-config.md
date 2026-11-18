# ADR 001: The answer prompt is versioned configuration

Date: 2026-11-18. Status: accepted. Workstream 5C.

## Context

The answer prompt, the repair prompt, the refusal text and the evidence formatting were
f-strings inside `app/core/generation.py`. A saved answer or Ragas score could not say which
prompt produced it, so a later prompt edit would silently make old and new numbers
incomparable. 5B is about to compare models; that comparison is only meaningful if the
prompt is held fixed and named in every result.

## Decision

- The prompt lives in `prompts/answer_v1.yaml`: version, refusal text, answer template,
  repair template, and the evidence block format (item template, separator, 24,000-character
  budget). Placeholders use `string.Template` (`${name}`) rather than `str.format`, because
  the prompt contains literal JSON braces and evidence text can contain `$` or `{}`.
- `app/core/prompts.py` loads it (`PROMPT_VERSION`, default `answer_v1`), checks the version
  field equals the file name, checks required placeholders, rejects path tricks, and computes
  a SHA-256 of the file with line endings normalised (Windows CRLF checkouts and Linux CI
  agree).
- A version is immutable. Any edit, including whitespace, is a new file (`answer_v2.yaml`).
  A test pins the v1 hash, so an edit fails CI.
- The version and hash are returned by `/answer`, recorded in the trace, saved in each answer
  run and copied onto each Ragas result row.

## Verification

- Snapshots of the answer and repair prompts were captured from the old code (commit
  2c61b69), with a `$` and braces in the evidence and enough text to hit the character cap.
  The new rendering matches byte for byte (`tests/test_prompts.py`).
- Mutation: changing one word in `answer_v1.yaml` fails 2 tests (hash and snapshot).
- The same tests pass on a copy with CRLF line endings.
- Full suite 46 passed; the real app starts on the full index (2,771 chunks).

## Alternatives considered

- **Python module with string constants**: simplest, but prompts stay mixed with code
  changes and nothing forces a new version on edit. Rejected.
- **Prompt registry / LangSmith / Langfuse prompt management**: real versioning and a UI, but
  adds a network dependency on the request path, an account, and a second source of truth
  outside git. Overkill for one prompt. Would become worth it with several prompts edited by
  non-engineers, or A/B tests in production.
- **Jinja2 templates**: loops and conditionals are not needed; `string.Template` is in the
  standard library and cannot execute code.

## Consequences

- Changing the prompt is now a reviewed config change: a new file, a new version, visible in
  the PR diff and in every result produced with it.
- Results collected before this change have `prompt_version: null`. They were produced by
  text identical to `answer_v1`, but that is not recorded in them, so they are not relabelled.
- Known limitation carried over unchanged (gap L6): the character budget can drop reranked
  chunks from the prompt while their IDs remain valid citations. Fixing it changes the prompt,
  so it would be `answer_v2`, decided with evidence in 5B.
