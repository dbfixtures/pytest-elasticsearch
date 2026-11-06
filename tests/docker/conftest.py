"""Fixtures for the tests against an Elasticsearch container."""

import pytest
from pytest import FixtureRequest

from pytest_elasticsearch.config import get_config


@pytest.fixture(autouse=True)
def skip_without_credentials(request: FixtureRequest) -> None:
    """Skip unless credentials for the container are configured."""
    config = get_config(request)
    if not (config.basic_auth or config.api_key):
        pytest.skip(
            "No credentials are configured for the Elasticsearch container: "
            "set --elasticsearch-basic-auth or --elasticsearch-api-key to run these tests."
        )
