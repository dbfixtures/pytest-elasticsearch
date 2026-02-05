"""Pytest-elasticsearch tests."""

from datetime import datetime

from elasticsearch import Elasticsearch
from pytest import FixtureRequest

import pytest_elasticsearch.config
from pytest_elasticsearch.executor import ElasticSearchExecutor


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

    assert not config["port"]
    assert config["host"] == "127.0.0.1"
    assert not config["cluster_name"]
    assert config["network_publish_host"] == "127.0.0.1"
    assert config["index_store_type"] == "mmapfs"


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
