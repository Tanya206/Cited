"""Run the four requested Ragas quality metrics on saved answer runs.

This is intentionally separate from CI: the metrics use an evaluator LLM and
therefore require credentials, network access, and incur API cost.
"""

import argparse
import json
import os
import sys
import types
from pathlib import Path

from dotenv import load_dotenv

from app.core.llm_client import get_llm_settings


class _LangChainEmbeddingAdapter:
    """Bridge Ragas' current text API to its older LangChain metric API."""

    def __init__(self, embeddings) -> None:
        self._embeddings = embeddings

    def embed_query(self, text: str) -> list[float]:
        return self._embeddings.embed_text(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embeddings.embed_texts(texts)


def _install_optional_vertex_shims() -> None:
    """Keep Ragas' optional Vertex imports from blocking Groq/OpenAI runs."""
    if "langchain_community.chat_models.vertexai" not in sys.modules:
        chat_module = types.ModuleType("langchain_community.chat_models.vertexai")
        chat_module.ChatVertexAI = type("ChatVertexAI", (), {})
        sys.modules[chat_module.__name__] = chat_module
    if "langchain_community.llms.vertexai" not in sys.modules:
        llm_module = types.ModuleType("langchain_community.llms.vertexai")
        llm_module.VertexAI = type("VertexAI", (), {})
        sys.modules[llm_module.__name__] = llm_module


def main() -> None:
    # Standalone evaluation commands do not pass through FastAPI's lifespan.
    # Load the same local environment configuration as the application.
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("eval/answer_runs.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("eval/ragas_results.json"))
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="evaluate only the first N usable answer runs (useful under provider quotas)",
    )
    parser.add_argument(
        "--contexts-per-sample",
        type=int,
        default=int(os.getenv("RAGAS_CONTEXTS_PER_SAMPLE", "6")),
        help="cap contexts sent to the evaluator to control prompt size",
    )
    args = parser.parse_args()

    try:
        _install_optional_vertex_shims()
        from ragas import EvaluationDataset, SingleTurnSample, evaluate
        from ragas.embeddings import HuggingFaceEmbeddings
        from ragas.llms import LangchainLLMWrapper
        from ragas.metrics import Faithfulness, LLMContextPrecisionWithoutReference, LLMContextRecall, ResponseRelevancy
        from ragas.run_config import RunConfig
        from langchain_openai import ChatOpenAI
    except ImportError as error:
        raise SystemExit(
            "Ragas could not load its evaluator dependencies. Run this command in a Python 3.11 environment: "
            "pip install -r requirements.txt; then retry. Original error: " + str(error)
        ) from error

    llm_settings = get_llm_settings()
    if not llm_settings.api_key:
        raise SystemExit("LLM_API_KEY (or legacy GROQ_API_KEY) is required for the Ragas evaluator.")

    rows = []
    invalid_lines = []
    for line_number, line in enumerate(args.input.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            invalid_lines.append(line_number)
    if invalid_lines:
        raise SystemExit(
            "The answer-runs JSONL contains malformed record lines: "
            f"{invalid_lines}. Run `python -m eval.collect_answer_runs --resume` "
            "to repair and complete the saved runs, then retry Ragas."
        )
    rows = [row for row in rows if not row.get("refused") and row.get("retrieved_contexts")]
    if args.limit is not None:
        if args.limit < 1:
            raise SystemExit("--limit must be at least 1")
        rows = rows[: args.limit]
    if args.contexts_per_sample < 1:
        raise SystemExit("--contexts-per-sample must be at least 1")
    for row in rows:
        row["retrieved_contexts"] = row["retrieved_contexts"][: args.contexts_per_sample]
    if not rows:
        raise SystemExit("No non-refusal answer runs with contexts were found.")

    dataset = EvaluationDataset(samples=[SingleTurnSample(**row) for row in rows])
    # An empty optional override must fall back to the shared model. Using
    # os.getenv(..., default) alone does not fall back when the variable exists
    # but is set to an empty string in .env.
    evaluator_model = os.getenv("RAGAS_MODEL") or llm_settings.model
    evaluator = ChatOpenAI(
        model=evaluator_model,
        api_key=os.getenv("RAGAS_API_KEY") or llm_settings.api_key,
        base_url=os.getenv("RAGAS_BASE_URL") or llm_settings.base_url,
        temperature=0,
        max_tokens=int(os.getenv("RAGAS_MAX_TOKENS", "4096")),
    )
    llm = LangchainLLMWrapper(evaluator)
    embeddings = _LangChainEmbeddingAdapter(
        HuggingFaceEmbeddings(
            model=os.getenv("RAGAS_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),
            use_api=False,
        )
    )
    metrics = [
        Faithfulness(llm=llm),
        ResponseRelevancy(
            llm=llm,
            strictness=int(os.getenv("RAGAS_RELEVANCY_STRICTNESS", "1")),
        ),
        LLMContextPrecisionWithoutReference(llm=llm),
        LLMContextRecall(llm=llm),
    ]
    # Do not silently turn evaluator/provider failures into NaN values. A NaN
    # report is not a quality score and is easy to misread as a result.
    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=llm,
        embeddings=embeddings,
        run_config=RunConfig(
            max_workers=int(os.getenv("RAGAS_MAX_WORKERS", "2")),
            max_retries=int(os.getenv("RAGAS_MAX_RETRIES", "3")),
        ),
        raise_exceptions=True,
    )
    payload = result.to_pandas().to_dict(orient="records") if hasattr(result, "to_pandas") else dict(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
