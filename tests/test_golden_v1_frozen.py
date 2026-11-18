import json

from eval.golden import GOLDEN_V1, answerable_items, content_sha256

# Pinned on 2026-11-18 when v1 was frozen. If this test fails, golden_v1.json was edited:
# revert it and put the change in golden_v2 instead.
GOLDEN_V1_SHA256 = "e55b4060c6adae7487c968ba55258f4dea89e69efe77d0a0add7210188bd34a1"


def test_golden_v1_is_frozen():
    assert content_sha256(GOLDEN_V1) == GOLDEN_V1_SHA256


def test_golden_v1_shape():
    dataset = json.loads(GOLDEN_V1.read_text(encoding="utf-8"))
    assert len(dataset["items"]) == 68
    assert len(answerable_items(dataset)) == 60
