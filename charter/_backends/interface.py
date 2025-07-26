from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from charter._ops import Operation

QueryType = TypeVar("QueryType", covariant=True)


class Backend(ABC, Generic[QueryType]):  # noqa: UP046
    """Abstract base class for query backends.

    Each backend transforms Operation objects into backend-specific
    query formats (e.g., MongoDB queries, SQLAlchemy expressions).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the backend.

        Args:
            args: Positional arguments for backend initialization
            kwargs: Keyword arguments for backend initialization
        """

    @abstractmethod
    def transform(self, operations: Sequence[Operation]) -> QueryType:
        """Transform operations into backend-specific query format.

        Args:
            operations: Sequence of operations to transform

        Returns:
            Backend-specific query object

        Raises:
            ValueError: If operations are invalid or unsupported
        """
        ...
