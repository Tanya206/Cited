from app.core.retrieval import reciprocal_rank_fusion


def result(chunk_id: str, rank: int, **extra: object) -> dict:
    return {
        "chunk_id": chunk_id,
        "doc_id": "paper-a",
        "page_number": 3,
        "chunk_type": "body_text",
        "text": f"text for {chunk_id}",
        "rank": rank,
        **extra,
    }


def test_rrf_rewards_a_chunk_found_by_both_retrievers() -> None:
    fused = reciprocal_rank_fusion(
        [
            [result("vector-only", 1), result("shared", 2)],
            [result("shared", 1, bm25_score=4.2), result("bm25-only", 2)],
        ],
        k=10,
    )

    assert fused[0]["chunk_id"] == "shared"
    assert fused[0]["ranks"] == {"vector": 2, "bm25": 1}
    assert fused[0]["found_by"] == ["vector", "bm25"]


def test_rrf_preserves_citation_metadata() -> None:
    fused = reciprocal_rank_fusion(
        [[result("table", 1, source_image_path="data/crops/table.png")], []]
    )

    assert fused[0]["doc_id"] == "paper-a"
    assert fused[0]["page_number"] == 3
    assert fused[0]["source_image_path"] == "data/crops/table.png"
