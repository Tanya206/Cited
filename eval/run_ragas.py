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
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("eval/answer_runs.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("eval/ragas_results.json"))
    args = parser.parse_args()

    try:
        _install_optional_vertex_shims()
        from ragas import EvaluationDataset, SingleTurnSample, evaluate
        from ragas.llms import llm_factory
        from ragas.metrics import Faithfulness, LLMContextPrecisionWithoutReference, LLMContextRecall, ResponseRelevancy
        from openai import AsyncOpenAI
    except ImportError as error:
        raise SystemExit(
            "Ragas could not load its evaluator dependencies. Run this command in a Python 3.11 environment: "
            "pip install -r requirements.txt; then retry. Original error: " + str(error)
        ) from error

    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit("GROQ_API_KEY is required for the Ragas evaluator.")

    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [row for row in rows if not row.get("refused") and row.get("retrieved_contexts")]
    if not rows:
        raise SystemExit("No non-refusal answer runs with contexts were found.")

    dataset = EvaluationDataset(samples=[SingleTurnSample(**row) for row in rows])
    client = AsyncOpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
    llm = llm_factory(os.getenv("RAGAS_MODEL", os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")), client=client)
    metrics = [
        Faithfulness(llm=llm),
        ResponseRelevancy(llm=llm),
        LLMContextPrecisionWithoutReference(llm=llm),
        LLMContextRecall(llm=llm),
    ]
    result = evaluate(dataset=dataset, metrics=metrics)
    payload = result.to_pandas().to_dict(orient="records") if hasattr(result, "to_pandas") else dict(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
