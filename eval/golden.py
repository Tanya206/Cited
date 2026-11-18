"""Golden set versions.

golden_v1 is frozen: the retrieval baseline of 2026-11-12 was measured on it, so it is never
edited. Fixes and new items go into golden_v2. A v1 number is never compared with a v2 number.
"""

import hashlib
import json
from pathlib import Path

GOLDEN_V1 = Path("eval/golden_v1.json")


def content_sha256(path: Path) -> str:
    """Hash of the parsed JSON, so line endings and whitespace do not change it."""
    data = json.loads(path.read_text(encoding="utf-8"))
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def answerable_items(dataset: dict) -> list[dict]:
    """Items scored by retrieval metrics: not refusal or clarification items."""
    return [
        item for item in dataset["items"]
        if not item.get("expects_refusal") and item.get("expected_outcome", "answer") == "answer"
    ]
