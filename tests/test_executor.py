"""Run tests for executor."""

from pathlib import Path

import mock
import pytest
from packaging.version import Version

from pytest_elasticsearch.executor import ElasticSearchExecutor

VERSION_STRING_8_0 = (
    "Version: 8.0.0, Build: default/tar/1b6a7ece17463df5ff54a3e1302d825889aa1161/"
    "2022-02-03T16:47:57.507843096Z, JVM: 17.0.1"
)
VERSION_STRING_8_15 = (
    "Version: 8.15.0, Build: default/tar/6f64a5184ddc8f708a2ddcc4ebf9d1d84b7f7e1b/"
    "2024-06-11T09:13:52.000000Z, JVM: 21.0.2"
)
VERSION_STRING_9_2 = (
    "Version: 9.2.0, Build: default/tar/1b6a7ece17463df5ff54a3e1302d825889aa1161/"
    "2025-03-11T09:13:52.000000Z, JVM: 21.0.2"
)


@pytest.mark.parametrize(
    "output, expected_version",
    (
        (VERSION_STRING_8_0, "8.0.0"),
        (VERSION_STRING_8_15, "8.15.0"),
        (VERSION_STRING_9_2, "9.2.0"),
    ),
)
def test_version_extraction(output: str, expected_version: str) -> None:
    """Verify if we can properly extract elasticsearch version."""
    with mock.patch(
        "pytest_elasticsearch.executor.check_output", lambda *args: output.encode("utf8")
    ):
        executor = ElasticSearchExecutor(
            executable=Path("elasticsearch"),
            host="127.0.0.1",
            port=8888,
            tcp_port=8889,
            pidfile=Path("elasticsearch.pid"),
            logs_path=Path("logs"),
            works_path=Path("works"),
            cluster_name="dontstart",
            network_publish_host="localhost",
            index_store_type="memory",
            timeout=10,
        )
        assert executor.version == Version(expected_version)
