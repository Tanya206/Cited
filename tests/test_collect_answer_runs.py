import requests

from eval.collect_answer_runs import _rate_limit_wait_seconds, _single_line


def _response(body: str) -> requests.Response:
    response = requests.Response()
    response.status_code = 502
    response._content = body.encode("utf-8")
    return response


def test_rate_limit_delay_is_parsed() -> None:
    response = _response(
        "rate_limit_exceeded: Please try again in 2m31.632s."
    )

    # 151.632 s rounds up: waiting less than the provider asked for just earns another 429.
    assert _rate_limit_wait_seconds(response) == 152


def test_non_rate_limit_response_returns_none() -> None:
    assert _rate_limit_wait_seconds(_response("upstream failed")) is None


def test_jsonl_records_normalize_nested_line_breaks() -> None:
    value = {"contexts": ["first line\nsecond line"]}

    assert _single_line(value) == {"contexts": ["first line second line"]}


def test_milliseconds_are_not_read_as_minutes() -> None:
    # Real Groq tokens-per-minute message seen in the 2026-11-19 pilot.
    body = "rate_limit_exceeded: ... on tokens per minute (TPM): Limit 8000. Please try again in 60ms."
    assert _rate_limit_wait_seconds(_response(body)) == 1


def test_seconds_hours_and_retry_after_header() -> None:
    assert _rate_limit_wait_seconds(_response("Rate limit reached. Please try again in 7.5s.")) == 8
    assert _rate_limit_wait_seconds(_response("rate_limit_exceeded: try again in 1h2m3s")) == 3723
    response = _response("rate_limit_exceeded: try again in 60ms")
    response.headers["Retry-After"] = "12"
    assert _rate_limit_wait_seconds(response) == 12
