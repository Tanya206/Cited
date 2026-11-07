"""Local cross-encoder reranking for the hybrid-retrieval candidates."""

from sentence_transformers import CrossEncoder
import re

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:
    """Load the model once and retain only the most query-relevant chunks."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: list[dict], top_k: int = 6) -> list[dict]:
        if not candidates:
            return []

        pairs = [(query, candidate["text"]) for candidate in candidates]
        scores = self.model.predict(pairs, show_progress_bar=False)
        table_query = bool(
            re.search(
                r"\b(table|batch size|learning rate|accuracy|precision|recall|f1|mIoU|score|error rate)\b",
                query,
                re.IGNORECASE,
            )
        )
        ranked = sorted(
            (
                {
                    **candidate,
                    # Cross-encoders often prefer explanatory prose to a
                    # compact table row; this small bonus preserves numeric
                    # evidence for table-oriented questions.
                    "rerank_score": float(score)
                    + (0.15 if table_query and candidate.get("chunk_type") == "table" else 0.0),
                }
                for candidate, score in zip(candidates, scores)
            ),
            key=lambda candidate: candidate["rerank_score"],
            reverse=True,
        )
        if table_query:
            table_candidates = [candidate for candidate in ranked if candidate.get("chunk_type") == "table"]
            if table_candidates and table_candidates[0] not in ranked[:top_k]:
                # Preserve one numeric/table candidate even when the model
                # assigns a low score to compact Markdown table text.
                ranked = [table_candidates[0]] + [candidate for candidate in ranked if candidate != table_candidates[0]]
        return ranked[:top_k]
