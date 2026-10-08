from app.core.query_validation import is_actionable_question


def test_bare_keywords_are_rejected() -> None:
    assert not is_actionable_question("satellite imagery")


def test_complete_questions_are_accepted() -> None:
    assert is_actionable_question("What is image segmentation?")
    assert is_actionable_question("Explain how SimCLR uses data augmentation")
