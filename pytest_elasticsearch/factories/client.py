"""Client fixture factory."""

from typing import Callable, Iterator

import pytest
from _pytest.fixtures import FixtureRequest
from elasticsearch import Elasticsearch
from elasticsearch import __version__ as elastic_version


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
            client = client.options(ignore_status=400)

        yield client
        for index in client.indices.get_alias():
            client.indices.delete(index=index)

    return elasticsearch_fixture
