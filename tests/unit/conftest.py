"""Fake elasticsearch fixtures."""

from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from unittest import mock

import pytest

from pytest_elasticsearch.executor import ElasticSearchExecutor

VERSION_STRING_9_2 = (
    "Version: 9.2.0, Build: default/tar/1b6a7ece17463df5ff54a3e1302d825889aa1161/"
    "2025-03-11T09:13:52.000000Z, JVM: 21.0.2"
)


def make_executor(port: int) -> ElasticSearchExecutor:
    """Build an executor without touching a real elasticsearch binary."""
    with mock.patch(
        "pytest_elasticsearch.executor.check_output",
        lambda *args: VERSION_STRING_9_2.encode("utf8"),
    ):
        return ElasticSearchExecutor(
            executable=Path("elasticsearch"),
            host="127.0.0.1",
            port=port,
            tcp_port=port + 1,
            pidfile=Path("elasticsearch.pid"),
            logs_path=Path("logs"),
            works_path=Path("works"),
            cluster_name="dontstart",
            network_publish_host="localhost",
            index_store_type="memory",
            timeout=10,
        )


class HealthHandler(BaseHTTPRequestHandler):
    """Answer every GET with the status code and body set on the server."""

    def do_GET(self) -> None:  # noqa: N802
        """Send the configured response."""
        code, body = self.server.response  # type: ignore[attr-defined]
        self.server.paths.append(self.path)  # type: ignore[attr-defined]
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body.encode("utf8"))

    def log_message(self, *args: object) -> None:
        """Keep the test output quiet."""


@pytest.fixture
def health_server() -> Iterator[HTTPServer]:
    """Run a fake elasticsearch health endpoint."""
    server = HTTPServer(("127.0.0.1", 0), HealthHandler)
    server.paths = []  # type: ignore[attr-defined]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()
