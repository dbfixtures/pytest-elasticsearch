"""Exceptions."""

from pathlib import Path
from typing import Self

from port_for import PortForException


class ElasticsearchRuntimeError(RuntimeError):
    """Elasticsearch runtime error."""

    @classmethod
    def invalid_executable(cls, *, executable: Path) -> Self:
        """Create an ElasticsearchRuntimeError from an invalid executable."""
        return cls(f"'{executable}' does not point to elasticsearch.")

    @classmethod
    def unrecognised_version(cls, *, output: str) -> Self:
        """Create an ElasticsearchRuntimeError from an unrecognised version."""
        return cls(
            "Elasticsearch version is not recognized. "
            "It is probably not supported. \n"
            f"Output is: {output}"
        )

    @classmethod
    def unsupported_version(cls, *, version: str) -> Self:
        """Create an ElasticsearchRuntimeError from an unsupported version."""
        return cls(f"Elasticsearch version '{version}' is not supported.")


class ElasticsearchPortForException(PortForException):
    """Elasticsearch port for exceptions."""

    @classmethod
    def already_used(cls, *, port: int, port_filename_path: Path) -> Self:
        """Port already in use."""
        return cls(
            f"Port {port} already in use, "
            f"probably by other instances of the test. "
            f"{port_filename_path} is already used."
        )

    @classmethod
    def all_attempts_failed(cls, count: int, ports: set[int]) -> Self:
        """All attempts to find a free port failed."""
        return cls(
            f"Attempted {count} times to select ports. "
            f"All attempted ports: {', '.join(map(str, ports))} are already "
            f"in use, probably by other instances of the test.",
        )
