"""Noproc fixture tests against an Elasticsearch container that requires authentication."""

import pytest
from elasticsearch import AuthenticationException, Elasticsearch

from pytest_elasticsearch import factories
from pytest_elasticsearch.executor import NoopElasticsearch

elasticsearch_docker = factories.elasticsearch("elasticsearch_nooproc")


def test_noproc_docker(elasticsearch_docker: Elasticsearch) -> None:
    """Index and search through the authenticated client fixture."""
    # Given
    elasticsearch_docker.index(
        index="docker-index", id="1", document={"text": "authenticated"}, refresh=True
    )

    # When
    res = elasticsearch_docker.search(index="docker-index", query={"match_all": {}})

    # Then
    assert res["hits"]["total"]["value"] == 1


def test_noproc_docker__unauthenticated(elasticsearch_nooproc: NoopElasticsearch) -> None:
    """Check that the container rejects a client without credentials."""
    # Given
    process = elasticsearch_nooproc
    client = Elasticsearch(hosts=[{"host": process.host, "port": process.port, "scheme": "http"}])

    # When / Then
    with pytest.raises(AuthenticationException):
        client.cluster.health()
