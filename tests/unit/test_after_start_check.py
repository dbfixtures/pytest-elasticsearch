"""Test ElasticSearchExecutor.after_start_check against a fake health endpoint."""

import json
from http.server import HTTPServer

import pytest

from pytest_elasticsearch.executor import ElasticSearchExecutor
from tests.unit.conftest import HealthHandler, make_executor


def health(status: str, *, timed_out: bool) -> str:
    """Render a cluster health response body."""
    return json.dumps({"cluster_name": "elasticsearch", "status": status, "timed_out": timed_out})


@pytest.mark.parametrize(
    "code, body, expected",
    (
        (200, health("green", timed_out=False), True),
        (200, health("yellow", timed_out=False), True),
        # documented behaviour since 8.0: a timed out wait still answers 200
        (200, health("red", timed_out=True), False),
        # behaviour observed in practice: a timed out wait answers 408
        (408, health("red", timed_out=True), False),
        (503, json.dumps({"error": {"type": "cluster_block_exception"}, "status": 503}), False),
        (200, "not json", False),
    ),
)
def test_after_start_check(
    health_server: HTTPServer, code: int, body: str, *, expected: bool
) -> None:
    """Report started only when the cluster health is at least yellow."""
    health_server.response = (code, body)  # type: ignore[attr-defined]
    executor = make_executor(port=health_server.server_address[1])
    assert executor.after_start_check() is expected
    assert health_server.paths == [ElasticSearchExecutor.HEALTH_PATH]  # type: ignore[attr-defined]


def test_after_start_check_nothing_listening() -> None:
    """Report not started when nothing answers on the port."""
    with HTTPServer(("127.0.0.1", 0), HealthHandler) as server:
        port = server.server_address[1]
    assert make_executor(port=port).after_start_check() is False
