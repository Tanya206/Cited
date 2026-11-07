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

    assert _rate_limit_wait_seconds(response) == 151


def test_non_rate_limit_response_returns_none() -> None:
    assert _rate_limit_wait_seconds(_response("upstream failed")) is None


def test_jsonl_records_normalize_nested_line_breaks() -> None:
    value = {"contexts": ["first line\nsecond line"]}

    assert _single_line(value) == {"contexts": ["first line second line"]}
