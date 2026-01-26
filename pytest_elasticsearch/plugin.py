# -*- coding: utf-8 -*-
# Copyright (C) 2016 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-elasticsearch.

# pytest-elasticsearch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-elasticsearch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-elasticsearch.  If not, see <http://www.gnu.org/licenses/>.
"""Pytest-elasticsearch py.test's plugin configuration."""

from pytest import Parser

from pytest_elasticsearch import factories

# pylint:disable=invalid-name
_help_host = "Elasticsearch host"
_help_executable = "Elasticsearch executable"
_help_port = "Elasticsearch port"
_help_cluster_name = "Cluster name of the elasticsearch process fixture"
_help_index_store_type = "type of the index to use in the elasticsearch process fixture"
_help_network_publish_host = "network host to which elasticsearch publish to connect to cluseter"
_help_elasticsearch_transport_tcp_port = "The tcp ansport port used \
    for internal communication between nodes within the cluster"


def pytest_addoption(parser: Parser) -> None:
    """Add plugin's configuration options."""
    parser.addini(name="elasticsearch_host", help=_help_host, default="127.0.0.1")

    parser.addini(
        name="elasticsearch_executable",
        help=_help_executable,
        default="/usr/share/elasticsearch/bin/elasticsearch",
    )

    parser.addini(name="elasticsearch_cluster_name", help=_help_cluster_name, default="")

    parser.addini(
        name="elasticsearch_index_store_type", help=_help_index_store_type, default="mmapfs"
    )

    parser.addini(
        name="elasticsearch_network_publish_host",
        help=_help_network_publish_host,
        default="127.0.0.1",
    )

    parser.addini(
        name="elasticsearch_port",
        help=_help_port,
        default=None,
    )

    parser.addini(
        "elasticsearch_transport_tcp_port",
        help=_help_elasticsearch_transport_tcp_port,
        default=None,
    )

    parser.addoption(
        "--elasticsearch-host",
        action="store",
        dest="elasticsearch_host",
        help=_help_host,
    )

    parser.addoption(
        "--elasticsearch-executable",
        action="store",
        dest="elasticsearch_executable",
        help=_help_executable,
    )

    parser.addoption(
        "--elasticsearch-cluster-name",
        action="store",
        dest="elasticsearch_cluster_name",
        help=_help_cluster_name,
    )

    parser.addoption(
        "--elasticsearch-index-store-type",
        action="store",
        dest="elasticsearch_index_store_type",
        help=_help_index_store_type,
    )

    parser.addoption(
        "--elasticsearch-network-publish-host",
        action="store",
        dest="elasticsearch_network_publish_host",
        help=_help_network_publish_host,
    )

    parser.addoption(
        "--elasticsearch-port", action="store", dest="elasticsearch_port", help=_help_port
    )

    parser.addoption(
        "--elasticsearch-transport-tcp-port",
        action="store",
        dest="elasticsearch_transport_tcp_port",
        help=_help_elasticsearch_transport_tcp_port,
    )


elasticsearch_proc = factories.elasticsearch_proc()
elasticsearch_nooproc = factories.elasticsearch_noproc()
elasticsearch = factories.elasticsearch("elasticsearch_proc")
