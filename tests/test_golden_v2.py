"""golden_v2 is v1 plus declared fixes plus new items; nothing else may differ."""

import json
from collections import Counter
from pathlib import Path

from eval.golden import GOLDEN_V1, content_sha256

GOLDEN_V2 = Path("eval/golden_v2.json")
TABLE_CATEGORIES = {"numeric_table", "numeric_table_text", "table_refusal"}


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_v2_records_which_v1_it_came_from():
    assert _load(GOLDEN_V2)["derived_from"]["content_sha256"] == content_sha256(GOLDEN_V1)


def test_v1_items_change_only_when_the_change_is_declared():
    v1 = {item["id"]: item for item in _load(GOLDEN_V1)["items"]}
    v2 = {item["id"]: item for item in _load(GOLDEN_V2)["items"]}
    assert set(v1) <= set(v2)
    for item_id, original in v1.items():
        if "changed_in_v2" not in v2[item_id]:
            assert v2[item_id] == original, f"{item_id} changed without a changed_in_v2 note"


def test_new_items_have_provenance_and_unique_ids():
    items = _load(GOLDEN_V2)["items"]
    ids = [item["id"] for item in items]
    assert len(ids) == len(set(ids))
    v1_ids = {item["id"] for item in _load(GOLDEN_V1)["items"]}
    for item in items:
        if item["id"] not in v1_ids:
            assert item["provenance"]["authored_by"] == "claude-code"
            assert isinstance(item["provenance"]["reviewed_by_owner"], bool)


def test_v2_has_at_least_20_table_questions():
    counts = Counter(item["category"] for item in _load(GOLDEN_V2)["items"])
    assert sum(counts[c] for c in TABLE_CATEGORIES) >= 20
