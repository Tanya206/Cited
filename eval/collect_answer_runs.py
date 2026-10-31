"""Collect answer outputs and contexts for an offline Ragas run.

The API remains the source of truth for retrieval, reranking, and generation;
this script only records its response plus the local chunk text needed by an
evaluator. It does not put corpus text into Git.
"""

import argparse
import json
import time
from pathlib import Path

import requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--dataset", type=Path, default=Path("eval/golden_dataset.json"))
    parser.add_argument("--chunks", type=Path, default=Path("data/chunks.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("eval/answer_runs.jsonl"))
    args = parser.parse_args()

    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    chunks = {
        row["chunk_id"]: row
        for row in (json.loads(line) for line in args.chunks.read_text(encoding="utf-8").splitlines())
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)

    with args.out.open("w", encoding="utf-8") as handle:
        for item in dataset["items"]:
            if item.get("expects_refusal") or item.get("expected_outcome", "answer") != "answer":
                continue

            payload = None
            for attempt in range(3):
                response = None
                try:
                    response = requests.post(
                        f"{args.base_url}/answer",
                        json={"query": item["question"], "retrieve_k": 50, "rerank_k": 12},
                        timeout=180,
                    )
                    if response.status_code in {500, 502, 503, 504} and attempt < 2:
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
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(item["id"], "contexts=", len(contexts), "refused=", record["refused"])


if __name__ == "__main__":
    main()