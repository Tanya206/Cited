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


class _LangfuseSpan:
    """Adapt Langfuse's context manager to the route's span interface."""

    def __init__(self, context_manager):
        self._context_manager = context_manager
        self._observation = None

    def __enter__(self):
        try:
            self._observation = self._context_manager.__enter__()
        except Exception:
            self._observation = None
        return self

    def __exit__(self, *args):
        try:
            return self._context_manager.__exit__(*args)
        except Exception:
            return False

    def update(self, **kwargs):
        if self._observation is None:
            return None
        try:
            self._observation.update(**kwargs)
        except Exception:
            return None
        return None


def answer_trace(query: str):
    if os.getenv("LANGFUSE_ENABLED", "true").lower() not in {"1", "true", "yes"}:
        return _NoopSpan()
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        return _NoopSpan()
    try:
        from langfuse import get_client

        client = get_client()
        return _LangfuseSpan(
            client.start_as_current_observation(
                as_type="span",
                name="cited.answer",
                input={"query": query},
            )
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
