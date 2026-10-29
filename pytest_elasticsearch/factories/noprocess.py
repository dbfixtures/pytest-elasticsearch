"""Noprocess fixture factory."""

from collections.abc import Callable, Iterator

import pytest
from _pytest.fixtures import FixtureRequest

from pytest_elasticsearch.config import get_config
from pytest_elasticsearch.exceptions import ElasticsearchConfigurationError
from pytest_elasticsearch.executor import NoopElasticsearch


def _basic_auth_pair(basic_auth: str | tuple[str, str] | None) -> tuple[str, str] | None:
    """Split a 'username:password' string into a username and password pair."""
    if not isinstance(basic_auth, str):
        return basic_auth
    user, sep, password = basic_auth.partition(":")
    if not sep:
        raise ElasticsearchConfigurationError.invalid_basic_auth()
    return user, password


def elasticsearch_noproc(
    host: str | None = None,
    port: int | None = None,
    *,
    basic_auth: str | tuple[str, str] | None = None,
    api_key: str | tuple[str, str] | None = None,
) -> Callable[[FixtureRequest], Iterator[NoopElasticsearch]]:
    """Elasticsearch noprocess factory.

    Credentials given here replace the ones from the configuration.

    :param host: hostname
    :param port: exact port (e.g. '8000', 8000)
    :param basic_auth: username and password, as a pair or as 'username:password'
    :param api_key: API key, encoded or as an (id, api_key) pair
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
        if basic_auth is not None or api_key is not None:
            es_basic_auth, es_api_key = basic_auth, api_key
        else:
            es_basic_auth, es_api_key = config.basic_auth, config.api_key
        if es_basic_auth and es_api_key:
            raise ElasticsearchConfigurationError.conflicting_authentication()

        yield NoopElasticsearch(
            host=es_host,
            port=es_port,
            basic_auth=_basic_auth_pair(es_basic_auth),
            api_key=es_api_key,
        )

    return elasticsearch_noproc_fixture
