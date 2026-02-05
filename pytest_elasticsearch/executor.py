"""Elasticsearch executor."""

import re
from pathlib import Path
from subprocess import check_output
from typing import Literal, Optional

from mirakuru import HTTPExecutor
from packaging.version import Version


class NoopElasticsearch:  # pylint:disable=too-few-public-methods
    """No operation Elasticsearch executor mock."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize Elasticsearch executor mock.

        :param str host: hostname under which elasticsearch is available
        :param int port: port under which elasticsearch is available.
        """
        self.host = host
        self.port = port

    @staticmethod
    def running() -> Literal[True]:
        """Mock method pretending the executor is running."""
        return True


# pylint:disable=too-many-instance-attributes
class ElasticSearchExecutor(HTTPExecutor):
    """Elasticsearch executor."""

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
        self._version: Optional[Version] = None
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
            f"http://{self.host}:{self.port}",
            timeout=timeout,
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
                    raise RuntimeError(
                        "Elasticsearch version is not recognized. "
                        "It is probably not supported. \n"
                        "Output is: " + output
                    )
                version = match.groupdict()
                self._version = Version(
                    ".".join([version["major"], version["minor"], version["patch"]])
                )
            except OSError as exc:
                raise RuntimeError(
                    "'%s' does not point to elasticsearch." % self.executable
                ) from exc
        return self._version

    def _exec_command(self) -> str:
        """Get command to run elasticsearch binary based on the version.

        :return: command to run elasticsearch
        """
        if self.version < Version("8.0.0"):
            raise RuntimeError("This elasticsearch version is not supported.")
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
