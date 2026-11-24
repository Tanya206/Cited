"""Collect answer outputs and contexts for an offline Ragas run.

The API remains the source of truth for retrieval, reranking, and generation;
this script only records its response plus the local chunk text needed by an
evaluator. It does not put corpus text into Git.
"""

import argparse
import json
import math
import re
import time
from datetime import date
from pathlib import Path

import requests

from eval.golden import content_sha256


_DURATION_PART = re.compile(r"(\d+(?:\.\d+)?)(ms|h|m|s)", re.I)
_UNIT_SECONDS = {"ms": 0.001, "s": 1.0, "m": 60.0, "h": 3600.0}


def _rate_limit_wait_seconds(response: requests.Response) -> int | None:
    """Extract the provider's suggested retry delay from an error response.

    Prefers the Retry-After header (the API passes on the provider's value with its 503),
    then Groq's message text: "try again in 2m31.632s", "7.5s" or "60ms". "ms" must be
    read before "m": reading "60ms" as 60 minutes once turned a 60 ms wait into an hour.
    """
    header = response.headers.get("Retry-After")
    if header and header.strip().isdigit():
        return max(1, int(header.strip()))
    body = response.text or ""
    if "rate_limit_exceeded" not in body and "Rate limit reached" not in body:
        return None
    match = re.search(r"try again in ((?:\d+(?:\.\d+)?(?:ms|h|m|s))+)", body, re.I)
    if not match:
        return None
    seconds = sum(
        float(amount) * _UNIT_SECONDS[unit.lower()] for amount, unit in _DURATION_PART.findall(match.group(1))
    )
    return max(1, math.ceil(seconds))


def _completed_ids(path: Path, retry_ids: set[str] | None = None) -> set[str]:
    """Read IDs already collected so a quota interruption can be resumed."""
    if not path.exists():
        return set()
    completed: set[str] = set()
    valid_lines: list[str] = []
    retry_ids = retry_ids or set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                # A process interruption can leave the final JSONL record
                # incomplete. Preserve valid records and repair the file so
                # later Ragas runs can read it normally.
                print("Ignoring an incomplete answer_runs.jsonl record while resuming.")
                continue
            # Escape Unicode line separators so splitlines() cannot mistake
            # them for JSONL record boundaries.
            if record["id"] in retry_ids:
                continue
            valid_lines.append(json.dumps(record, ensure_ascii=True))
            completed.add(record["id"])
    repaired = "\n".join(valid_lines)
    if repaired:
        repaired += "\n"
    path.write_text(repaired, encoding="utf-8")
    return completed


def _single_line(value):
    """Normalize nested strings so every JSONL record occupies one line."""
    if isinstance(value, str):
        return value.replace("\r", " ").replace("\n", " ")
    if isinstance(value, list):
        return [_single_line(item) for item in value]
    if isinstance(value, dict):
        return {key: _single_line(item) for key, item in value.items()}
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--dataset", type=Path, default=Path("eval/golden_v2.json"))
    parser.add_argument("--chunks", type=Path, default=Path("data/chunks.jsonl"))
    # A new default file: the 2026-11-03 runs predate the index rebuild and record no config.
    parser.add_argument("--out", type=Path, default=Path("eval/answer_runs_v2.jsonl"))
    parser.add_argument("--ids", default="", help="comma-separated golden IDs to collect (for a pilot)")
    # Served defaults (app/models/schemas.py). The old hard-coded 50/12 evaluated a
    # configuration nobody serves (gap H3).
    parser.add_argument("--retrieve-k", type=int, default=20)
    parser.add_argument("--rerank-k", type=int, default=6)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="append results and skip golden items already present in --out",
    )
    parser.add_argument(
        "--wait-for-rate-limit",
        action="store_true",
        help="wait for the provider-suggested delay before retrying a rate limit",
    )
    parser.add_argument(
        "--retry-id",
        action="append",
        default=[],
        help="recollect a specific previously saved item (repeatable)",
    )
    args = parser.parse_args()

    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    dataset_sha256 = content_sha256(args.dataset)
    wanted = {item_id.strip() for item_id in args.ids.split(",") if item_id.strip()}
    chunks = {
        row["chunk_id"]: row
        for row in (json.loads(line) for line in args.chunks.read_text(encoding="utf-8").splitlines())
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)

    retry_ids = set(args.retry_id)
    completed = _completed_ids(args.out, retry_ids) if args.resume else set()
    mode = "a" if args.resume else "w"
    with args.out.open(mode, encoding="utf-8") as handle:
        for item in dataset["items"]:
            if item.get("expects_refusal") or item.get("expected_outcome", "answer") != "answer":
                continue
            if wanted and item["id"] not in wanted:
                continue
            if item["id"] in completed:
                print(item["id"], "already collected; skipping")
                continue

            payload = None
            for attempt in range(3):
                response = None
                try:
                    response = requests.post(
                        f"{args.base_url}/answer",
                        json={"query": item["question"], "retrieve_k": args.retrieve_k, "rerank_k": args.rerank_k},
                        timeout=180,
                    )
                    if response.status_code in {500, 502, 503, 504} and attempt < 2:
                        wait_seconds = _rate_limit_wait_seconds(response)
                        if wait_seconds is not None:
                            if not args.wait_for_rate_limit:
                                raise RuntimeError(
                                    f"Groq rate limit reached. Retry after approximately "
                                    f"{wait_seconds} seconds, then resume with "
                                    f"--resume. Response: {response.text[:500]}"
                                )
                            print(
                                f"{item['id']} Groq rate limit; waiting "
                                f"{wait_seconds}s before retrying..."
                            )
                            time.sleep(wait_seconds)
                            continue
                        print(f"{item['id']} temporary HTTP {response.status_code}; retrying...")
                        time.sleep(2 ** attempt)
                        continue
                    response.raise_for_status()
                    payload = response.json()
                    break
                except requests.RequestException as error:
                    if attempt == 2:
                        detail = response.text[:1000] if response is not None else "no response body"
                        raise RuntimeError(
                            f"{item['id']} failed for question {item['question']!r}: {error}; body={detail}"
                        ) from error
                    print(f"{item['id']} request error; retrying...")
                    time.sleep(2 ** attempt)

            if payload is None:
                raise RuntimeError(f"{item['id']} returned no answer payload")

            contexts = [
                chunks[cid]["text"]
                for cid in payload.get("reranked_chunk_ids", [])
                if cid in chunks
            ]
            expected_contexts = [entry["quote"] for entry in item.get("evidence", [])]
            record = {
                "id": item["id"],
                "user_input": item["question"],
                "response": payload["answer"],
                "retrieved_contexts": contexts,
                "reference": item["reference_answer"],
                "reference_contexts": expected_contexts,
                "refused": payload.get("refused", False),
                # Which prompt produced this answer; carried into the Ragas results.
                "prompt_version": payload.get("prompt_version"),
                "prompt_sha256": payload.get("prompt_sha256"),
                "generator_model": payload.get("generator_model"),
                "generator_usage": payload.get("usage", {}),
                "retrieve_k": args.retrieve_k,
                "rerank_k": args.rerank_k,
                "dataset": str(args.dataset).replace("\\", "/"),
                "dataset_sha256": dataset_sha256,
                "collected_on": date.today().isoformat(),
            }
            handle.write(json.dumps(_single_line(record), ensure_ascii=True) + "\n")
            print(item["id"], "contexts=", len(contexts), "refused=", record["refused"])


if __name__ == "__main__":
    main()
