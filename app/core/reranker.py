"""Local cross-encoder reranking for the hybrid-retrieval candidates."""

from sentence_transformers import CrossEncoder

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
        ranked = sorted(
            (
                {**candidate, "rerank_score": float(score)}
                for candidate, score in zip(candidates, scores)
            ),
            key=lambda candidate: candidate["rerank_score"],
            reverse=True,
        )
        return ranked[:top_k]
