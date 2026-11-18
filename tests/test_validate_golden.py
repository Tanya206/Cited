import json

from eval.validate_golden import validate


def _item(item_id, page=3, quote="contrastive loss"):
    return {
        "id": item_id,
        "question": "What loss does it use?",
        "category": "method",
        "expects_refusal": False,
        "expected_doc_ids": ["paper-a"],
        "expected_pages": [3],
        "evidence": [{"doc_id": "paper-a", "page_number": page, "quote": quote}],
    }


def _write(tmp_path, items):
    path = tmp_path / "golden.json"
    path.write_text(json.dumps({"items": items}), encoding="utf-8")
    return path


def test_structure_only_accepts_valid_file_without_index(tmp_path):
    assert validate(_write(tmp_path, [_item("G1")]), None, strict=False) == 0


def test_structure_only_rejects_duplicate_ids(tmp_path):
    assert validate(_write(tmp_path, [_item("G1"), _item("G1")]), None, strict=False) == 1


def test_structure_only_rejects_evidence_outside_expected_pages(tmp_path):
    assert validate(_write(tmp_path, [_item("G1", page=9)]), None, strict=False) == 1


def test_structure_only_rejects_empty_quote(tmp_path):
    assert validate(_write(tmp_path, [_item("G1", quote="")]), None, strict=False) == 1
