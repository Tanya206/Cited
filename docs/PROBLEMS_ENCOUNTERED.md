# Problems Encountered

## Groq organization token quota

During the full answer evaluation, the API completed multiple golden items and
then returned HTTP 502 for a later item. The response body showed Groq error
code `rate_limit_exceeded` and a tokens-per-day (TPD) limit for the configured
organization and model.

This was not a retrieval or application-startup failure. The FastAPI route was
running, retrieval completed, and the upstream answer provider rejected a new
request because the organization quota was exhausted.

The evaluation collector now:

- Detects the provider quota message even when it is wrapped in HTTP 502.
- Shows the provider's suggested retry delay.
- Supports `--resume` so completed items are not rerun and charged again.
- Supports `--wait-for-rate-limit` when an automatic wait is appropriate.

Recommended recovery:

```powershell
python -m eval.collect_answer_runs --resume
```

To wait automatically for the provider's suggested delay:

```powershell
python -m eval.collect_answer_runs --resume --wait-for-rate-limit
```

The quota is organization-level, so creating another API key in the same
Groq organization does not create an independent token budget.
