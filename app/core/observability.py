"""Optional Langfuse tracing for one complete answer request.

Tracing must never be required for the product to answer.  Missing keys,
missing package, or a tracing failure therefore degrade to a no-op span.
"""

from contextlib import nullcontext
import os


class _NoopSpan:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def update(self, **_kwargs):
        return None


def answer_trace(query: str):
    if os.getenv("LANGFUSE_ENABLED", "true").lower() not in {"1", "true", "yes"}:
        return _NoopSpan()
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        return _NoopSpan()
    try:
        from langfuse import get_client

        client = get_client()
        return client.start_as_current_observation(
            as_type="span",
            name="cited.answer",
            input={"query": query},
        )
    except Exception:
        return _NoopSpan()


def flush_traces() -> None:
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        return
    try:
        from langfuse import get_client

        get_client().flush()
    except Exception:
        return
