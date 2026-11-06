"""Test how the noprocess fixture resolves its credentials."""

import pytest
from pytest import Pytester


def make_noproc_test(pytester: Pytester, factory_arguments: str, assertions: str = "") -> None:
    """Write a test module that uses a noprocess fixture built with the given arguments."""
    pytester.makepyfile(
        f"""
        from pytest_elasticsearch import factories

        noproc = factories.elasticsearch_noproc({factory_arguments})

        def test_noproc(noproc):
            {assertions or "pass"}
        """
    )


@pytest.mark.parametrize(
    "factory_arguments, options, basic_auth, api_key",
    (
        ("", [], None, None),
        ('basic_auth="elastic:fake-password"', [], ("elastic", "fake-password"), None),
        ('basic_auth=("elastic", "fake-password")', [], ("elastic", "fake-password"), None),
        (
            'api_key="fake-api-key"',
            ["--elasticsearch-basic-auth=config:fake-password"],
            None,
            "fake-api-key",
        ),
        (
            "",
            ["--elasticsearch-basic-auth=config:fake-password"],
            ("config", "fake-password"),
            None,
        ),
        ("", ["--elasticsearch-api-key=fake-config-api-key"], None, "fake-config-api-key"),
    ),
)
def test_elasticsearch_noproc__credentials(
    pytester: Pytester,
    factory_arguments: str,
    options: list[str],
    basic_auth: tuple[str, str] | None,
    api_key: str | None,
) -> None:
    """Take credentials from the factory, or else from the configuration."""
    # Given
    make_noproc_test(
        pytester,
        factory_arguments,
        f"assert (noproc.basic_auth, noproc.api_key) == {(basic_auth, api_key)!r}",
    )

    # When
    result = pytester.runpytest(*options)

    # Then
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    "factory_arguments, options, message",
    (
        (
            'basic_auth="elastic:fake-password", api_key="fake-api-key"',
            [],
            "Both basic_auth and api_key are set. Set only one of them.",
        ),
        (
            "",
            [
                "--elasticsearch-basic-auth=config:fake-password",
                "--elasticsearch-api-key=fake-config-api-key",
            ],
            "Both basic_auth and api_key are set. Set only one of them.",
        ),
        (
            'basic_auth="elastic"',
            [],
            "basic_auth is not in the 'username:password' format.*",
        ),
    ),
)
def test_elasticsearch_noproc__raises(
    pytester: Pytester,
    factory_arguments: str,
    options: list[str],
    message: str,
) -> None:
    """Reject settings the client could not use."""
    # Given
    make_noproc_test(pytester, factory_arguments)

    # When
    result = pytester.runpytest(*options)

    # Then
    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines([f"*ElasticsearchConfigurationError: {message}"])
