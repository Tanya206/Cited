"""Shared fixture: run generate_cited_answer against a fake provider and capture the prompts."""

from types import SimpleNamespace

QUESTION = "How does SimCLR use data augmentation? (cost $5, {braces})"

CHUNKS = [
    {"chunk_id": "simclr_c0001", "doc_id": "simclr", "page_number": 3,
     "text": "SimCLR composes random crop, colour distortion and blur. Loss uses ${tau} and {x}."},
    {"chunk_id": "simclr_c0002", "doc_id": "simclr", "page_number": 4,
     "text": "Table 1: | Aug | Top-1 |\n| crop+colour | 64.5 |"},
    # Large chunks so the 24,000-character evidence budget cuts the list.
    *[
        {"chunk_id": f"filler_c{i:04d}", "doc_id": "filler", "page_number": i,
         "text": "filler text " * 900}
        for i in range(1, 5)
    ],
]


def capture_prompts(generation_module, monkeypatch):
    """Return the user messages sent: [answer prompt, repair prompt]."""
    replies = iter([
        '{"answer": "Uses crops.", "citation_chunk_ids": ["not-a-real-id"]}',
        '{"answer": "Uses crops.", "citation_chunk_ids": ["simclr_c0001"]}',
    ])
    sent = []

    def create(**request):
        sent.append(request["messages"][0]["content"])
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=next(replies)))])

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    settings = SimpleNamespace(api_key="test", model="m", max_tokens=10)
    monkeypatch.setattr(generation_module, "create_llm_client", lambda: (client, settings))
    result = generation_module.generate_cited_answer(QUESTION, CHUNKS)
    return sent, result
