"""Pytest-elasticsearch tests."""

from datetime import datetime
from typing import cast

from elasticsearch import Elasticsearch
from pytest import FixtureRequest, MonkeyPatch

import pytest_elasticsearch.config
from pytest_elasticsearch.executor import ElasticSearchExecutor
from pytest_elasticsearch.factories.client import _cleanup_indices


def test_elastic_process(elasticsearch_proc: ElasticSearchExecutor) -> None:
    """Simple test for starting elasticsearch_proc."""
    assert elasticsearch_proc.running() is True


def test_elasticsearch(elasticsearch: Elasticsearch) -> None:
    """Test if elasticsearch fixtures connects to process."""
    info = elasticsearch.cluster.health()
    assert info["status"] == "green"


def test_default_configuration(request: FixtureRequest) -> None:
    """Test default configuration."""
    config = pytest_elasticsearch.config.get_config(request)

    assert not config.port
    assert config.host == "127.0.0.1"
    assert not config.cluster_name
    assert config.network_publish_host == "127.0.0.1"
    assert config.index_store_type == "mmapfs"


def test_external_elastic(
    elasticsearch2: Elasticsearch,
    elasticsearch2_noop: Elasticsearch,
) -> None:
    """Check that nooproc connects to the same redis."""
    elasticsearch2.indices.create(index="test-index")
    doc = {
        "author": "kimchy",
        "text": "Elasticsearch: cool. bonsai cool.",
        "timestamp": datetime.utcnow(),
    }
    res = elasticsearch2.index(index="test-index", id="1", document=doc)
    assert res["result"] == "created"

    res = elasticsearch2_noop.get(index="test-index", id="1")
    assert res["found"] is True
    elasticsearch2.indices.refresh(index="test-index")

    res = elasticsearch2_noop.search(index="test-index", query={"match_all": {}})
    assert res["hits"]["total"]["value"] == 1


def test_cleanup_removes_user_index_after_fixture_teardown(
    elasticsearch: Elasticsearch, monkeypatch: MonkeyPatch
) -> None:
    """Ensure cleanup deletes user indices even when system indices are present.

    Given an Elasticsearch client with a user index and a mocked system index
    When cleanup runs against the aliased index list
    Then the user index is removed
    """
    index_name = "cleanup-user-index"
    elasticsearch.indices.create(index=index_name)
    elasticsearch.indices.refresh(index=index_name)

    original_get_alias = elasticsearch.indices.get_alias

    def get_alias_with_system() -> dict[str, object]:
        aliases = dict(original_get_alias())
        aliases[".system-index"] = {}
        return aliases

    monkeypatch.setattr(elasticsearch.indices, "get_alias", get_alias_with_system)

    _cleanup_indices(elasticsearch)
    exists_response = elasticsearch.indices.exists(index=index_name)
    assert exists_response.meta.status == 404


def test_cleanup_skips_system_indices() -> None:
    """Ensure cleanup skips system indices while deleting user indices.

    Given a client whose alias list includes system and user indices
    When cleanup runs
    Then only user indices are deleted
    """
    deleted: list[str] = []

    class _DummyIndices:
        def get_alias(self) -> dict[str, object]:
            return {".system-index": {}, "user-index": {}}

        def delete(self, index: str) -> None:
            deleted.append(index)

    class _DummyClient:
        indices = _DummyIndices()

    _cleanup_indices(cast(Elasticsearch, _DummyClient()))
    assert deleted == ["user-index"]
