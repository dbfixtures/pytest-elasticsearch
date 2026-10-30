"""Test how the noprocess fixture resolves its connection settings."""

import pytest
from pytest import FixtureRequest, MonkeyPatch

from pytest_elasticsearch import factories
from pytest_elasticsearch.exceptions import ElasticsearchConfigurationError
from pytest_elasticsearch.executor import NoopElasticsearch

# Session fixtures are cached, so each case gets its own fixture.
noproc_default = factories.elasticsearch_noproc()
noproc_basic_auth_string = factories.elasticsearch_noproc(basic_auth="elastic:fake-password")
noproc_basic_auth_pair = factories.elasticsearch_noproc(basic_auth=("elastic", "fake-password"))
noproc_api_key = factories.elasticsearch_noproc(api_key="fake-api-key")
noproc_config_basic_auth = factories.elasticsearch_noproc()
noproc_config_api_key = factories.elasticsearch_noproc()
noproc_both_credentials = factories.elasticsearch_noproc(
    basic_auth="elastic:fake-password", api_key="fake-api-key"
)
noproc_config_both_credentials = factories.elasticsearch_noproc()
noproc_invalid_basic_auth = factories.elasticsearch_noproc(basic_auth="elastic")


@pytest.mark.parametrize(
    "fixture_name, options, basic_auth, api_key",
    (
        ("noproc_default", {}, None, None),
        ("noproc_basic_auth_string", {}, ("elastic", "fake-password"), None),
        ("noproc_basic_auth_pair", {}, ("elastic", "fake-password"), None),
        (
            "noproc_api_key",
            {"elasticsearch_basic_auth": "config:fake-password"},
            None,
            "fake-api-key",
        ),
        (
            "noproc_config_basic_auth",
            {"elasticsearch_basic_auth": "config:fake-password"},
            ("config", "fake-password"),
            None,
        ),
        (
            "noproc_config_api_key",
            {"elasticsearch_api_key": "fake-config-api-key"},
            None,
            "fake-config-api-key",
        ),
    ),
)
def test_elasticsearch_noproc__credentials(
    request: FixtureRequest,
    monkeypatch: MonkeyPatch,
    fixture_name: str,
    options: dict[str, str],
    basic_auth: tuple[str, str] | None,
    api_key: str | None,
) -> None:
    """Take credentials from the factory, or else from the configuration."""
    # Given
    for option, value in options.items():
        monkeypatch.setattr(request.config.option, option, value)

    # When
    process: NoopElasticsearch = request.getfixturevalue(fixture_name)

    # Then
    assert process.basic_auth == basic_auth
    assert process.api_key == api_key


@pytest.mark.parametrize(
    "fixture_name, options, message",
    (
        ("noproc_both_credentials", {}, "Both basic_auth and api_key are set"),
        (
            "noproc_config_both_credentials",
            {
                "elasticsearch_basic_auth": "config:fake-password",
                "elasticsearch_api_key": "fake-config-api-key",
            },
            "Both basic_auth and api_key are set",
        ),
        ("noproc_invalid_basic_auth", {}, "basic_auth is not in the 'username:password' format"),
    ),
)
def test_elasticsearch_noproc__raises(
    request: FixtureRequest,
    monkeypatch: MonkeyPatch,
    fixture_name: str,
    options: dict[str, str],
    message: str,
) -> None:
    """Reject settings the client could not use."""
    # Given
    for option, value in options.items():
        monkeypatch.setattr(request.config.option, option, value)

    # When / Then
    with pytest.raises(ElasticsearchConfigurationError, match=message):
        request.getfixturevalue(fixture_name)
