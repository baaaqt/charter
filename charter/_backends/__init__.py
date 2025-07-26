"""Backend implementations for different query engines."""

from typing import TYPE_CHECKING, Any, Literal, overload

from charter._backends.interface import Backend
from charter._exc import BackendNotAvailableError

__all__ = ["Backend"]


if TYPE_CHECKING:
    try:
        from charter._backends.pymongo import PymongoBackend
        from charter._backends.sqlalchemy import SQLAlchemyBackend
    except ImportError:
        pass

    @overload
    def load_backend(
        name: Literal["sqlalchemy"],
    ) -> "type[SQLAlchemyBackend]": ...

    @overload
    def load_backend(
        name: Literal["pymongo"],
    ) -> "type[PymongoBackend]": ...

    def load_backend(name: str) -> "type[Backend[Any]]": ...
else:

    def load_backend(name: str) -> Backend[Any]:
        match name:
            case "sqlalchemy":
                try:
                    from charter._backends.sqlalchemy import SQLAlchemyBackend
                except ImportError as e:
                    raise BackendNotAvailableError(
                        "Backend 'sqlalchemy' is required for SQLAlchemyBackend."
                        " Install with: `pip install sqlalchemy`",
                    ) from e

                return SQLAlchemyBackend

            case "pymongo":
                try:
                    from charter._backends.pymongo import PymongoBackend
                except ImportError as e:
                    raise BackendNotAvailableError(
                        "Backend 'pymongo' is required for PymongoBackend."
                        " Install with: `pip install pymongo`",
                    ) from e
                return PymongoBackend
            case _:
                raise ValueError(f"Unknown backend: {name}")
