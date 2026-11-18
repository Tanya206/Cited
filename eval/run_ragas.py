"""Score saved answer runs with the four Ragas metrics, one (item, metric) at a time.

Separate from CI: the metrics call a judge LLM, which needs credentials and network and is
not deterministic.

Resumable: every (item, metric) result is appended to the output JSONL as soon as it is
scored, and pairs already in the file are skipped. A quota error therefore loses nothing.
Each record names the judge, the embedding model, the generator, the prompt version and the
dataset, and counts the judge calls and tokens it used, so the cost of a full run can be
measured on a pilot before anyone pays for it.

    python -m eval.run_ragas --ids G09,G10,G27,G60,G106
"""

import argparse
import json
import os
import sys
import types
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

from app.core.llm_client import get_llm_settings

# Fields Ragas scores. Everything else in an answer-run record is metadata about the run.
SAMPLE_FIELDS = ("user_input", "response", "retrieved_contexts", "reference", "reference_contexts")
RUN_METADATA_FIELDS = ("id", "prompt_version", "prompt_sha256", "generator_model", "dataset_sha256")

# Run order from the brief: cheapest and most important first.
METRIC_ORDER = ("faithfulness", "llm_context_precision_without_reference", "answer_relevancy", "context_recall")
JUDGE_VARIABLES = ("RAGAS_API_KEY", "RAGAS_BASE_URL", "RAGAS_MODEL")
EMBEDDING_MODEL_DEFAULT = "BAAI/bge-small-en-v1.5"


def sample_fields(row: dict) -> dict:
    """Keep only what Ragas scores, so run metadata never reaches the metric prompts."""
    return {key: row[key] for key in SAMPLE_FIELDS if key in row}


def resolve_judge(env: Mapping[str, str], generator) -> dict:
    """Judge settings: all three RAGAS_* variables together, or none (then share the generator).

    Setting only some of them used to mix providers: a judge key could be sent to the
    generator's URL (gap S5). That is now an error.
    """
    present = [name for name in JUDGE_VARIABLES if env.get(name)]
    if present and len(present) < len(JUDGE_VARIABLES):
        missing = [name for name in JUDGE_VARIABLES if name not in present]
        raise SystemExit(
            f"Set {', '.join(JUDGE_VARIABLES)} together. Missing: {', '.join(missing)}. "
            "A partial judge configuration could send one provider's key to another provider."
        )
    if present:
        return {"api_key": env["RAGAS_API_KEY"], "base_url": env["RAGAS_BASE_URL"],
                "model": env["RAGAS_MODEL"], "shares_generator_quota": False}
    return {"api_key": generator.api_key, "base_url": generator.base_url,
            "model": generator.model, "shares_generator_quota": True}


def completed_pairs(path: Path) -> set[tuple[str, str]]:
    """(item id, metric) pairs already scored in the output file."""
    if not path.exists():
        return set()
    done = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            done.add((record["id"], record["metric"]))
    return done


def select_metrics(requested: str) -> list[str]:
    names = [name.strip() for name in requested.split(",") if name.strip()] or list(METRIC_ORDER)
    unknown = [name for name in names if name not in METRIC_ORDER]
    if unknown:
        raise SystemExit(f"Unknown metric(s): {unknown}. Choose from {METRIC_ORDER}.")
    return [name for name in METRIC_ORDER if name in names]


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


def _usage_counter():
    """A LangChain callback that counts judge calls and the tokens the provider reports."""
    from langchain_core.callbacks import BaseCallbackHandler

    class UsageCounter(BaseCallbackHandler):
        def __init__(self) -> None:
            self.reset()

        def reset(self) -> None:
            self.calls = self.prompt_tokens = self.completion_tokens = 0

        def on_llm_end(self, response, **_kwargs) -> None:
            self.calls += 1
            usage = (response.llm_output or {}).get("token_usage") or {}
            self.prompt_tokens += int(usage.get("prompt_tokens") or 0)
            self.completion_tokens += int(usage.get("completion_tokens") or 0)

    return UsageCounter()


def main() -> None:
    # Standalone evaluation commands do not pass through FastAPI's lifespan.
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("eval/answer_runs_v2.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("eval/results/ragas_runs.jsonl"))
    parser.add_argument("--ids", default="", help="comma-separated golden IDs (for a pilot)")
    parser.add_argument("--metrics", default="", help=f"comma-separated subset of {METRIC_ORDER}")
    parser.add_argument("--limit", type=int, default=None, help="first N usable answer runs only")
    parser.add_argument(
        "--contexts-per-sample",
        type=int,
        default=int(os.getenv("RAGAS_CONTEXTS_PER_SAMPLE", "6")),
        help="cap contexts sent to the judge to control prompt size",
    )
    args = parser.parse_args()
    metric_names = select_metrics(args.metrics)

    try:
        _install_optional_vertex_shims()
        import ragas
        from ragas import EvaluationDataset, SingleTurnSample, evaluate
        from ragas.embeddings import HuggingFaceEmbeddings
        from ragas.llms import LangchainLLMWrapper
        from ragas.metrics import Faithfulness, LLMContextPrecisionWithoutReference, LLMContextRecall, ResponseRelevancy
        from ragas.run_config import RunConfig
        from langchain_openai import ChatOpenAI
        import openai
    except ImportError as error:
        raise SystemExit("Ragas could not load its evaluator dependencies: " + str(error)) from error

    judge = resolve_judge(os.environ, get_llm_settings())
    if not judge["api_key"]:
        raise SystemExit("No judge key: set RAGAS_API_KEY, RAGAS_BASE_URL and RAGAS_MODEL (or LLM_API_KEY).")
    if judge["shares_generator_quota"]:
        print("WARNING: no RAGAS_* judge configured; the judge shares the generator's model and quota.")

    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    wanted = {item_id.strip() for item_id in args.ids.split(",") if item_id.strip()}
    skipped_refused = [row["id"] for row in rows if row.get("refused")]
    rows = [row for row in rows if not row.get("refused") and row.get("retrieved_contexts")]
    if wanted:
        rows = [row for row in rows if row["id"] in wanted]
    if args.limit is not None:
        rows = rows[: args.limit]
    if not rows:
        raise SystemExit("No non-refusal answer runs with contexts matched the selection.")
    if skipped_refused:
        # Faithfulness of a refusal is undefined; these are scored by the refusal script instead.
        print(f"Not scored (answer was a refusal): {', '.join(skipped_refused)}")

    counter = _usage_counter()
    evaluator = ChatOpenAI(
        model=judge["model"], api_key=judge["api_key"], base_url=judge["base_url"], temperature=0,
        max_tokens=int(os.getenv("RAGAS_MAX_TOKENS", "4096")), callbacks=[counter],
    )
    llm = LangchainLLMWrapper(evaluator)
    embedding_model = os.getenv("RAGAS_EMBEDDING_MODEL", EMBEDDING_MODEL_DEFAULT)
    embeddings = _LangChainEmbeddingAdapter(HuggingFaceEmbeddings(model=embedding_model, use_api=False))
    metrics = {
        "faithfulness": Faithfulness(llm=llm),
        "llm_context_precision_without_reference": LLMContextPrecisionWithoutReference(llm=llm),
        "answer_relevancy": ResponseRelevancy(
            llm=llm, strictness=int(os.getenv("RAGAS_RELEVANCY_STRICTNESS", "1"))
        ),
        "context_recall": LLMContextRecall(llm=llm),
    }
    run_config = RunConfig(
        max_workers=int(os.getenv("RAGAS_MAX_WORKERS", "2")),
        max_retries=int(os.getenv("RAGAS_MAX_RETRIES", "3")),
    )

    done = completed_pairs(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("a", encoding="utf-8") as handle:
        for row in rows:
            row["retrieved_contexts"] = row["retrieved_contexts"][: args.contexts_per_sample]
            sample = SingleTurnSample(**sample_fields(row))
            for name in metric_names:
                if (row["id"], name) in done:
                    print(f"{row['id']} {name}: already scored, skipping")
                    continue
                counter.reset()
                # raise_exceptions=True on purpose: a provider failure must stop the run, not
                # become a NaN that looks like a score. Finished pairs are already saved.
                try:
                    result = evaluate(
                        dataset=EvaluationDataset(samples=[sample]), metrics=[metrics[name]], llm=llm,
                        embeddings=embeddings, run_config=run_config, raise_exceptions=True,
                        show_progress=False,
                    )
                except openai.NotFoundError as error:
                    raise SystemExit(
                        f"Judge returned 404 at {judge['base_url']!r} for model {judge['model']!r}. "
                        "Check RAGAS_BASE_URL (OpenAI-compatible URLs usually end in /v1) and RAGAS_MODEL. "
                        f"Scores already saved in {args.output} are kept."
                    ) from error
                score = float(result.to_pandas()[name].iloc[0])
                record = {
                    **{key: row.get(key) for key in RUN_METADATA_FIELDS},
                    "metric": name,
                    "score": score,
                    "judge_model": judge["model"],
                    "judge_host": urlparse(judge["base_url"]).netloc,
                    "judge_shares_generator_quota": judge["shares_generator_quota"],
                    "embedding_model": embedding_model if name == "answer_relevancy" else None,
                    "contexts_scored": len(row["retrieved_contexts"]),
                    "judge_calls": counter.calls,
                    "judge_prompt_tokens": counter.prompt_tokens,
                    "judge_completion_tokens": counter.completion_tokens,
                    "ragas_version": ragas.__version__,
                    "scored_on": date.today().isoformat(),
                }
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                handle.flush()
                print(f"{row['id']} {name}: {score:.3f} ({counter.calls} calls, "
                      f"{counter.prompt_tokens}+{counter.completion_tokens} tokens)")


if __name__ == "__main__":
    main()
