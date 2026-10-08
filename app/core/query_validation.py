"""Small deterministic guard for ambiguous corpus searches."""

QUESTION_STARTS = (
    "what ", "how ", "why ", "when ", "where ", "who ", "which ",
    "is ", "are ", "can ", "does ", "do ", "explain ", "define ",
    "describe ", "compare ", "summarize ", "list ", "give ", "tell me ",
)


def is_actionable_question(query: str) -> bool:
    """Reject bare keywords while accepting ordinary research questions."""
    normalized = " ".join(query.lower().split())
    return (
        len(normalized.split()) >= 3
        and (normalized.endswith("?") or normalized.startswith(QUESTION_STARTS))
    )
