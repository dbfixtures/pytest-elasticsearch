"""Process fixture factory."""

import shutil
from pathlib import Path
from typing import Callable, Iterable, Iterator, Optional

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.tmpdir import TempPathFactory
from mirakuru import ProcessExitedWithError
from port_for import PortForException, PortType, get_port

from pytest_elasticsearch.config import ElasticsearchConfig, get_config
from pytest_elasticsearch.executor import ElasticSearchExecutor


def _elasticsearch_port(
    port: Optional[PortType], config: ElasticsearchConfig, excluded_ports: Iterable[int]
) -> int:
    """User specified port, otherwise find an unused port from config."""
    elasticsearch_port = get_port(port, excluded_ports) or get_port(config.port, excluded_ports)
    assert elasticsearch_port is not None
    return elasticsearch_port


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
        elasticsearch_host = host or config.host
        elasticsearch_executable = executable or config.executable

        port_path = tmp_path_factory.getbasetemp()
        if hasattr(request.config, "workerinput"):
            port_path = tmp_path_factory.getbasetemp().parent

        n = 0
        used_ports: set[int] = set()
        while True:
            try:
                elasticsearch_port = _elasticsearch_port(port, config, used_ports)
                port_filename_path = port_path / f"elastic-{elasticsearch_port}.port"
                if elasticsearch_port in used_ports:
                    raise PortForException(
                        f"Port {elasticsearch_port} already in use, "
                        f"probably by other instances of the test. "
                        f"{port_filename_path} is already used."
                    )
                used_ports.add(elasticsearch_port)
                with port_filename_path.open("x") as port_file:
                    port_file.write(f"elasticsearch_port {elasticsearch_port}\n")
                break
            except FileExistsError:
                n += 1
                if n >= config.port_search_count:
                    raise PortForException(
                        f"Attempted {n} times to select ports. "
                        f"All attempted ports: {', '.join(map(str, used_ports))} are already "
                        f"in use, probably by other instances of the test."
                    ) from None
        assert elasticsearch_port
        elasticsearch_transport_port = get_port(
            transport_tcp_port, exclude_ports=[elasticsearch_port]
        ) or get_port(config.transport_tcp_port, exclude_ports=[elasticsearch_port])
        assert elasticsearch_transport_port

        elasticsearch_cluster_name = (
            cluster_name or config.cluster_name or f"elasticsearch_cluster_{elasticsearch_port}"
        )
        assert elasticsearch_cluster_name
        elasticsearch_index_store_type = index_store_type or config.index_store_type
        elasticsearch_network_publish_host = network_publish_host or config.network_publish_host
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
