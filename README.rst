
.. image:: https://raw.githubusercontent.com/dbfixtures/pytest-elasticsearch/master/logo.png
    :width: 100px
    :height: 100px

pytest-elasticsearch
====================

.. image:: https://img.shields.io/pypi/v/pytest-elasticsearch.svg
    :target: https://pypi.python.org/pypi/pytest-elasticsearch/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/wheel/pytest-elasticsearch.svg
    :target: https://pypi.python.org/pypi/pytest-elasticsearch/
    :alt: Wheel Status

.. image:: https://img.shields.io/pypi/pyversions/pytest-elasticsearch.svg
    :target: https://pypi.python.org/pypi/pytest-elasticsearch/
    :alt: Supported Python Versions

.. image:: https://img.shields.io/pypi/l/pytest-elasticsearch.svg
    :target: https://pypi.python.org/pypi/pytest-elasticsearch/
    :alt: License

What is this?
=============

This is a pytest plugin that enables you to test your code that relies on a running Elasticsearch search engine.
It allows you to specify fixtures for Elasticsearch process and client fixtures.


.. image:: https://raw.githubusercontent.com/dbfixtures/pytest-elasticsearch/main/docs/images/architecture.svg
    :alt: Project Architecture Diagram
    :align: center

How to use
==========

.. warning::

    This plugin requires at least version 8.0 of elasticsearch to work.

Prerequisites
-------------

Install Elasticsearch 8.x or newer following the official documentation:
https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html

.. note::

    Elasticsearch enables security features by default. If your instance requires
    authentication or TLS, configure it accordingly (or disable security for local
    testing per Elasticsearch docs).

Quickstart: first test
----------------------

1) Install the plugin and your test dependencies (as you normally do for your project).
2) Ensure Elasticsearch is available (local install or container).
3) Create a test that uses the built-in fixture:

.. code-block:: python

    def test_can_connect(elasticsearch):
        assert elasticsearch.info()

4) Run your tests:

.. code-block:: shell

    pytest

The plugin contains three fixtures:

* **elasticsearch** - a client fixture that has function-scope, and which
  cleans Elasticsearch at the end of each test.
* **elasticsearch_proc** - a session-scoped fixture that starts an Elasticsearch
  instance at its first use and stops at the end of the tests.
* **elasticsearch_nooproc** - a no-process fixture that holds connection data
  to an already running Elasticsearch instance

Simply include one of these fixtures in your test fixture list.

You can also create additional Elasticsearch client and process fixtures if you need to:


.. code-block:: python

    from pytest_elasticsearch import factories

    elasticsearch_my_proc = factories.elasticsearch_proc(port=None)
    elasticsearch_my = factories.elasticsearch('elasticsearch_my_proc')

.. note::

    Each Elasticsearch process fixture can be configured in a different way than
    the others through the fixture factory arguments.

.. note::

    Managed Elasticsearch processes use ``tmp_path_factory`` for their data paths
    and are cleaned up automatically. When using ``elasticsearch_nooproc``, the
    running instance (and its data directories) are managed by you.


Connecting to already existing Elasticsearch service
----------------------------------------------------

Some projects use already running Elasticsearch servers
(e.g., in Docker). To connect to them, use the
``elasticsearch_nooproc`` fixture.

.. code-block:: python

    es_external = factories.elasticsearch_noproc(
        host="localhost",
        port=9200,
        basic_auth=("elastic", "<your_password>"),
    )
    elasticsearch = factories.elasticsearch("es_external")

Configure the host/port to match your running Elasticsearch instance using the
options below. If not provided, the noprocess fixture defaults to port **9200**.
You may provide basic_auth or the api_key. If none is provided, to authentication is assumed.

Configuration
=============

You can define your settings in three ways: fixture factory arguments, command line options,
and pytest.ini configuration options.
You can pick which you prefer, but remember that these settings are handled in the following order:

1. Fixture factory argument
2. Command line option
3. Configuration option in your pytest.ini file

.. list-table:: Configuration options
   :header-rows: 1

   * - Elasticsearch option
     - Fixture factory argument
     - Command line option
     - pytest.ini option
     - Noop process fixture
     - Default
   * - Elasticsearch executable
     - executable
     - --elasticsearch-executable
     - elasticsearch_executable
     -
     - /usr/share/elasticsearch/bin/elasticsearch
   * - host
     - host
     - --elasticsearch-host
     - elasticsearch_host
     - host
     - 127.0.0.1
   * - port
     - port
     - --elasticsearch-port
     - elasticsearch_port
     - port (default 9200)
     - random (free port)
   * - Free port search count
     - port_search_count
     - --elasticsearch-port-search-count
     - elasticsearch_port_search_count
     - -
     - 5
   * - Elasticsearch cluster name
     - cluster_name
     - --elasticsearch-cluster-name
     - elasticsearch_cluster_name
     - -
     - elasticsearch_cluster_<port>
   * - index storage type
     - index_store_type
     - --elasticsearch-index-store-type
     - elasticsearch_index_store_type
     - -
     - mmapfs
   * - network publish host
     - network_publish_host
     - --elasticsearch-network-publish-host
     - elasticsearch_network_publish_host
     - -
     - 127.0.0.1
   * - Transport TCP port
     - transport_tcp_port
     - --elasticsearch-transport-tcp-port
     - elasticsearch_transport_tcp_port
     - -
     - random

Example usage:

* pass it as an argument to your own fixture

    .. code-block:: python

        elasticsearch_proc = factories.elasticsearch_proc(
            cluster_name='awsome_cluster')


* specify your cluster name as ``elasticsearch_cluster_name`` in your ``pytest.ini`` file.

    To do so, put a line like the following under the ``[pytest]`` section of your ``pytest.ini``:

    .. code-block:: ini

        [pytest]
        elasticsearch_cluster_name = awsome_cluster

Known issues
------------

It might happen that the process can't be started due to lack of permissions.
The files that the user running tests must have access to are:

* /etc/default/elasticsearch

Make sure you either run tests as a user who has access to these files,
or grant the user proper permissions or add them to the proper groups.

In CI, we install Elasticsearch from tar/zip archives,
which do not set up additional permission restrictions, so it's not a problem on the CI/CD.

Package resources
-----------------

* Bug tracker: https://github.com/dbfixtures/pytest-elasticsearch/issues
