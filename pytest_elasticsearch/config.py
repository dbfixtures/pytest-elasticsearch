"""Configuration for pytest-elasticsearch."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pytest import FixtureRequest


@dataclass
class ElasticsearchConfig:
    """Elasticsearch configuration."""

    executable: Path
    host: str
    port: int | None
    port_search_count: int
    transport_tcp_port: int | None
    cluster_name: str
    network_publish_host: str
    index_store_type: str
    api_key: str | None
    basic_auth: str | None


def get_config(request: FixtureRequest) -> ElasticsearchConfig:
    """Return an ElasticsearchConfig instance with config options."""

    def get_elasticsearch_option(option: str) -> Any:
        name = "elasticsearch_" + option
        return request.config.getoption(name) or request.config.getini(name)

    return ElasticsearchConfig(
        executable=get_elasticsearch_option("executable"),
        host=get_elasticsearch_option("host"),
        port=get_elasticsearch_option("port"),
        port_search_count=int(get_elasticsearch_option("port_search_count")),
        transport_tcp_port=get_elasticsearch_option("transport_tcp_port"),
        cluster_name=get_elasticsearch_option("cluster_name"),
        network_publish_host=get_elasticsearch_option("network_publish_host"),
        index_store_type=get_elasticsearch_option("index_store_type"),
        api_key=get_elasticsearch_option("api_key"),
        basic_auth=get_elasticsearch_option("basic_auth"),
    )
