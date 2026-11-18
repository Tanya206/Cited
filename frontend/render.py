"""HTML helpers for the Streamlit UI.

Anything that comes from the model or the corpus is escaped before it is placed inside
HTML. The answer text is shaped by the user's question and by text in the papers, so
rendering it raw would let either one inject markup or script into the page.
"""

import html


def answer_card_html(answer: str) -> str:
    """Return the answer as escaped text inside the styled card, keeping line breaks."""
    safe = html.escape(answer, quote=True).replace("\n", "<br>")
    return f"<div class='answer-card'><p>{safe}</p></div>"
