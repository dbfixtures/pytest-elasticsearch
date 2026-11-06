"""Elasticsearch executor."""

import json
import re
from http.client import HTTPConnection, HTTPException
from logging import getLogger
from pathlib import Path
from subprocess import check_output
from typing import Literal

from mirakuru import HTTPExecutor
from packaging.version import Version

from pytest_elasticsearch.exceptions import ElasticsearchRuntimeError

LOG = getLogger(__name__)


class NoopElasticsearch:  # pylint:disable=too-few-public-methods
    """No operation Elasticsearch executor mock."""

    def __init__(
        self,
        host: str,
        port: int,
        *,
        api_key: str | tuple[str, str] | None = None,
        basic_auth: tuple[str, str] | None = None,
    ) -> None:
        """Initialize Elasticsearch executor mock.

        :param str host: hostname under which elasticsearch is available
        :param int port: port under which elasticsearch is available.
        :param api_key: API key, encoded or as an (id, api_key) pair
        :param basic_auth: username and password pair
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        self.basic_auth = basic_auth

    @staticmethod
    def running() -> Literal[True]:
        """Mock method pretending the executor is running."""
        return True


# pylint:disable=too-many-instance-attributes
class ElasticSearchExecutor(HTTPExecutor):
    """Elasticsearch executor."""

    HEALTH_PATH = "/_cluster/health?wait_for_status=yellow&timeout=1s"
    """Cluster health request with defined minimum required status."""

    HEALTH_REQUEST_TIMEOUT = 5
    """Connection timeout for a single health request."""

    def __init__(
        self,
        executable: Path,
        host: str,
        port: int,
        tcp_port: int,
        pidfile: Path,
        logs_path: Path,
        works_path: Path,
        cluster_name: str,
        network_publish_host: str,
        index_store_type: str,
        timeout: int,
    ) -> None:  # pylint:disable=too-many-arguments
        """Initialize ElasticSearchExecutor.

        :param executable: Executable path
        :param host: hostname under which elasticsearch will be running
        :param port: port elasticsearch listens on
        :param tcp_port: port used for internal communication
        :param pidfile: pidfile location
        :param logs_path: log files location
        :param works_path: workdir location
        :param cluster_name: cluster name
        :param network_publish_host: network host to which elasticsearch
            publish to connect to cluseter'
        :param index_store_type: type of the index to use in the
            elasticsearch process fixture
        :param timeout: Time after which to give up to start elasticsearch
        """
        self._version: Version | None = None
        self.executable = executable
        self.host = host
        self.port = port
        # TODO: rename to transport_port
        self.tcp_port = tcp_port
        self.pidfile = pidfile
        self.logs_path = logs_path
        self.works_path = works_path
        self.cluster_name = cluster_name
        self.network_publish_host = network_publish_host
        self.index_store_type = index_store_type
        super().__init__(
            self._exec_command(),
            f"http://{self.host}:{self.port}{self.HEALTH_PATH}",
            method="GET",
            timeout=timeout,
        )

    def after_start_check(self) -> bool:
        """Check if the cluster is at least yellow.

        Elasticsearch serves http before it recovers the cluster state and
        rejects nearly every request until then - so the port answering is not
        enough. Only the health body says whether the wait succeeded.
        """
        conn = HTTPConnection(self.host, self.port, timeout=self.HEALTH_REQUEST_TIMEOUT)
        try:
            conn.request("GET", self.HEALTH_PATH)
            body = conn.getresponse().read()
        except (HTTPException, OSError) as ex:
            LOG.debug("Encounter %s while trying to check if elasticsearch has started.", ex)
            return False
        finally:
            conn.close()

        try:
            health = json.loads(body)
        except ValueError:
            return False
        # the status code of a timed out wait is 200 in the docs, but 408 in practice
        return (
            isinstance(health, dict)
            and health.get("timed_out") is False
            and health.get("status") in ("yellow", "green")
        )

    @property
    def version(self) -> Version:
        """Get the given elasticsearch executable version parts.

        :return: Elasticsearch version
        """
        if not self._version:
            try:
                output = check_output([self.executable, "-Vv"]).decode("utf-8")
                match = re.search(r"Version: (?P<major>\d)\.(?P<minor>\d+)\.(?P<patch>\d+)", output)
                if not match:
                    raise ElasticsearchRuntimeError.unrecognised_version(
                        output=output,
                    )
                version = match.groupdict()
                self._version = Version(
                    ".".join([version["major"], version["minor"], version["patch"]])
                )
            except OSError as exc:
                raise ElasticsearchRuntimeError.invalid_executable(
                    executable=self.executable,
                ) from exc
        return self._version

    def _exec_command(self) -> str:
        """Get command to run elasticsearch binary based on the version.

        :return: command to run elasticsearch
        """
        if self.version < Version("8.0.0"):
            raise ElasticsearchRuntimeError.unsupported_version(
                version=str(self.version),
            )
        return f"""
            {self.executable} -p {self.pidfile}
            -E http.port={self.port}
            -E transport.port={self.tcp_port}
            -E path.logs={self.logs_path}
            -E path.data={self.works_path}
            -E cluster.name={self.cluster_name}
            -E network.host='{self.network_publish_host}'
            -E index.store.type={self.index_store_type}
            -E xpack.security.enabled=false
        """
