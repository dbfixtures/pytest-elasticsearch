# Copyright (C) 2013-2016 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-elasticsearch.

# pytest-elasticsearch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-elasticsearch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-elasticsearch.  If not, see <http://www.gnu.org/licenses/>.
"""Fixture factories."""

import shutil
from pathlib import Path
from typing import Callable, Iterator, Optional

import pytest
from elasticsearch import Elasticsearch
from elasticsearch import __version__ as elastic_version
from mirakuru import ProcessExitedWithError
from port_for import get_port
from port_for.api import PortType
from pytest import FixtureRequest, TempPathFactory

from pytest_elasticsearch.config import get_config
from pytest_elasticsearch.executor import ElasticSearchExecutor, NoopElasticsearch


def elasticsearch_proc(
    executable: Optional[Path] = None,
    host: Optional[str] = None,
    port: Optional[PortType] = -1,
    transport_tcp_port: Optional[PortType] = None,
    cluster_name: Optional[str] = None,
    network_publish_host: Optional[str] = None,
    index_store_type: Optional[str] = None,
) -> Callable[[FixtureRequest, TempPathFactory], Iterator[ElasticSearchExecutor]]:
    """Create elasticsearch process fixture.

    :param executable: elasticsearch's executable
    :param host: host that the instance listens on
    :param port:
        exact port (e.g. '8000', 8000)
        randomly selected port (None) - any random available port
        [(2000,3000)] or (2000,3000) - random available port from a given range
        [{4002,4003}] or {4002,4003} - random of 4002 or 4003 ports
        [(2000,3000), {4002,4003}] -random of given range and set
    :param transport_tcp_port: Port used for communication between nodes
    :param cluster_name: name of a cluser this node should work on.
        Used for autodiscovery. By default each node is in it's own cluser.
    :param network_publish_host: host to publish itself within cluser
        http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/modules-network.html
    :param index_store_type: index.store.type setting. *memory* by default
        to speed up tests
    """

    @pytest.fixture(scope="session")
    def elasticsearch_proc_fixture(
        request: FixtureRequest, tmp_path_factory: TempPathFactory
    ) -> Iterator[ElasticSearchExecutor]:
        """Elasticsearch process starting fixture."""
        config = get_config(request)
        elasticsearch_host = host or config["host"]
        elasticsearch_executable = executable or config["executable"]

        elasticsearch_port = get_port(port) or get_port(config["port"])
        assert elasticsearch_port
        elasticsearch_transport_port = get_port(
            transport_tcp_port, exclude_ports=[elasticsearch_port]
        ) or get_port(config["transport_tcp_port"], exclude_ports=[elasticsearch_port])
        assert elasticsearch_transport_port

        elasticsearch_cluster_name = (
            cluster_name or config["cluster_name"] or f"elasticsearch_cluster_{elasticsearch_port}"
        )
        assert elasticsearch_cluster_name
        elasticsearch_index_store_type = index_store_type or config["index_store_type"]
        elasticsearch_network_publish_host = network_publish_host or config["network_publish_host"]
        tmpdir = tmp_path_factory.mktemp(f"pytest-elasticsearch-{request.fixturename}")

        logs_path = tmpdir / "logs"

        pidfile = tmpdir / f"elasticsearch.{elasticsearch_port}.pid"
        work_path = tmpdir / f"workdir_{elasticsearch_port}"

        elasticsearch_executor = ElasticSearchExecutor(
            elasticsearch_executable,
            elasticsearch_host,
            elasticsearch_port,
            elasticsearch_transport_port,
            pidfile,
            logs_path,
            work_path,
            elasticsearch_cluster_name,
            elasticsearch_network_publish_host,
            elasticsearch_index_store_type,
            timeout=60,
        )

        elasticsearch_executor.start()
        yield elasticsearch_executor
        try:
            elasticsearch_executor.stop()
        except ProcessExitedWithError:
            pass
        shutil.rmtree(work_path)
        shutil.rmtree(logs_path)

    return elasticsearch_proc_fixture


def elasticsearch_noproc(
    host: Optional[str] = None, port: Optional[int] = None
) -> Callable[[FixtureRequest], Iterator[NoopElasticsearch]]:
    """Elasticsearch noprocess factory.

    :param host: hostname
    :param port: exact port (e.g. '8000', 8000)
    :returns: function which makes a elasticsearch process
    """

    @pytest.fixture(scope="session")
    def elasticsearch_noproc_fixture(request: FixtureRequest) -> Iterator[NoopElasticsearch]:
        """Noop Process fixture for PostgreSQL.

        :param FixtureRequest request: fixture request object
        :rtype: pytest_dbfixtures.executors.TCPExecutor
        :returns: tcp executor-like object
        """
        config = get_config(request)
        es_host = host or config["host"]
        assert es_host
        es_port = port or config["port"] or 9300
        assert es_port

        yield NoopElasticsearch(host=es_host, port=es_port)

    return elasticsearch_noproc_fixture


def elasticsearch(process_fixture_name: str) -> Callable[[FixtureRequest], Iterator[Elasticsearch]]:
    """Create Elasticsearch client fixture.

    :param process_fixture_name: elasticsearch process fixture name
    """

    @pytest.fixture
    def elasticsearch_fixture(request: FixtureRequest) -> Iterator[Elasticsearch]:
        """Elasticsearch client fixture."""
        process = request.getfixturevalue(process_fixture_name)
        if not process.running():
            process.start()
        client = Elasticsearch(
            hosts=[{"host": process.host, "port": process.port, "scheme": "http"}],
            request_timeout=30,
            verify_certs=False,
        )
        if elastic_version >= (8, 0, 0):
            client.options(ignore_status=400)

        yield client
        for index in client.indices.get_alias():
            client.indices.delete(index=index)

    return elasticsearch_fixture
