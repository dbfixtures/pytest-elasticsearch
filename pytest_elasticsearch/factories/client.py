"""Client fixture factory."""

from typing import Callable, Iterator

import pytest
from _pytest.fixtures import FixtureRequest
from elasticsearch import Elasticsearch
from elasticsearch import __version__ as elastic_version


def _cleanup_indices(client: Elasticsearch) -> None:
    """Delete user-created indices while skipping system indices."""
    for index in client.indices.get_alias():
        if index.startswith("."):
            continue
        client.indices.delete(index=index)


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
            api_key=process.api_key,
            basic_auth=process.basic_auth,
            request_timeout=process.request_timeout,
            verify_certs=process.verify_certs,
        )
        if elastic_version >= (8, 0, 0):
            client = client.options(ignore_status=400)

        yield client
        _cleanup_indices(client)

    return elasticsearch_fixture
