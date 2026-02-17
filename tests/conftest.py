"""Tests main conftest file."""

import warnings

from pytest_elasticsearch import factories

warnings.simplefilter("error", category=DeprecationWarning)


elasticsearch_proc2 = factories.elasticsearch_proc(port=9393)
elasticsearch_nooproc2 = factories.elasticsearch_noproc(port=9393)

elasticsearch2 = factories.elasticsearch("elasticsearch_proc2")
elasticsearch2_noop = factories.elasticsearch("elasticsearch_nooproc2")
# pylint:enable=invalid-name
