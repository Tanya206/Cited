from frontend.render import answer_card_html


def test_model_html_is_escaped():
    html = answer_card_html('<img src=x onerror="alert(1)"> and <script>alert(2)</script>')
    assert "<img" not in html
    assert "<script" not in html
    assert "&lt;img" in html and "&lt;script&gt;" in html


def test_plain_answer_keeps_text_and_line_breaks():
    html = answer_card_html("SimCLR uses two views.\nThen a contrastive loss & a projection head.")
    assert html.startswith("<div class='answer-card'><p>")
    assert "two views.<br>Then" in html
    assert "&amp; a projection head" in html


def test_streamlit_app_renders_model_html_as_text():
    """Run the real UI script with an attacker-shaped answer; no live API needed."""
    from streamlit.testing.v1 import AppTest

    # AppTest resolves relative paths against this test file, not the working directory.
    app = AppTest.from_file("../frontend/streamlit_app.py", default_timeout=30)
    app.session_state["answer_data"] = {
        "answer": '<img src=x onerror="alert(1)">Evidence says X.',
        "refused": False,
        "retrieved_count": 20,
        "reranked_count": 6,
        "citations": [],
    }
    app.run()
    assert not app.exception
    cards = [block.value for block in app.markdown if block.value.startswith("<div class='answer-card'>")]
    assert cards == ["<div class='answer-card'><p>&lt;img src=x onerror=&quot;alert(1)&quot;&gt;Evidence says X.</p></div>"]
