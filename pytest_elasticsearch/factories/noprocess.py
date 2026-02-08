"""Noprocess fixture factory."""

from typing import Callable, Iterator

import pytest
from _pytest.fixtures import FixtureRequest

from pytest_elasticsearch.config import get_config
from pytest_elasticsearch.executor import NoopElasticsearch


def elasticsearch_noproc(
    host: str | None = None, port: int | None = None
) -> Callable[[FixtureRequest], Iterator[NoopElasticsearch]]:
    """Elasticsearch noprocess factory.

    :param host: hostname
    :param port: exact port (e.g. '8000', 8000)
    :returns: function which makes a elasticsearch process
    """

    @pytest.fixture(scope="session")
    def elasticsearch_noproc_fixture(request: FixtureRequest) -> Iterator[NoopElasticsearch]:
        """Noop Process fixture for Elasticsearch.

        :param FixtureRequest request: fixture request object
        :returns: tcp executor-like object
        """
        config = get_config(request)
        es_host = host or config.host
        assert es_host
        es_port = port or config.port or 9300
        assert es_port

        yield NoopElasticsearch(host=es_host, port=es_port)

    return elasticsearch_noproc_fixture
