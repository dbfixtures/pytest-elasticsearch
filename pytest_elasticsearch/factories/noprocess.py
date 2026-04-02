"""Noprocess fixture factory."""

from typing import Callable, Iterator

import pytest
from _pytest.fixtures import FixtureRequest

from pytest_elasticsearch.config import get_config
from pytest_elasticsearch.executor import NoopElasticsearch


def elasticsearch_noproc(
    host: str | None = None,
    port: int | None = None,
    basic_auth: str | tuple[str, str] | None = None,
    api_key: str | tuple[str, str] | None = None,
    request_timeout: float = 30.0,
    verify_certs: bool = False,
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
        es_port = port or config.port or 9200
        assert es_port
        es_basic_auth = basic_auth
        if es_basic_auth is None:
            es_basic_auth = config.basic_auth
        if isinstance(es_basic_auth, str):
            user, sep, password = es_basic_auth.partition(":")
            if not sep:
                raise ValueError(
                    "elasticsearch_basic_auth must be in the format 'username:password'"
                )
            es_basic_auth = (user, password)
        es_api_key = api_key or config.api_key

        yield NoopElasticsearch(
            host=es_host,
            port=es_port,
            basic_auth=es_basic_auth,
            api_key=es_api_key,
            request_timeout=request_timeout,
            verify_certs=verify_certs,
        )

    return elasticsearch_noproc_fixture
