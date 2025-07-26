from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Any, Literal


class OperationType(Enum):
    """Discriminator for operation types."""

    OPERATOR = "operator"
    LOGIC = "logic"


class Operators(StrEnum):
    EQ = "eq"
    IN = "in"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    CONTAINS = "contains"
    REGEX = "regex"


class LogicOperators(StrEnum):
    AND = "and"
    OR = "or"
    NOT = "not"


@dataclass(slots=True, frozen=True)
class ContainsData:
    """Data for contains operation with case sensitivity option."""

    value: str
    ignore_case: bool = False

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Contains value cannot be empty string")


class Operation(ABC):
    """Base class for all query operations."""

    @property
    @abstractmethod
    def operation_type(self) -> OperationType:
        """Get the type of operation for type discrimination."""
        ...

    @abstractmethod
    def __post_init__(self) -> None:
        """Validate operation parameters."""
        ...


@dataclass(slots=True, frozen=True)
class Operator(Operation):
    """Basic field operation (eq, gt, contains, etc.)."""

    operator: Operators
    field: str
    value: Any

    @property
    def operation_type(self) -> Literal[OperationType.OPERATOR]:
        return OperationType.OPERATOR

    def __post_init__(self) -> None:
        if not self.field:
            raise ValueError("Field name cannot be empty")

        if self.operator == Operators.IN:
            if not isinstance(self.value, Sequence) or isinstance(self.value, str):
                raise ValueError("IN operator requires a sequence value")
            if len(self.value) == 0:
                raise ValueError("IN operator cannot have empty sequence")

        if self.operator == Operators.CONTAINS:
            if not isinstance(self.value, ContainsData):
                raise ValueError("CONTAINS operator requires ContainsData value")


@dataclass(slots=True, frozen=True)
class LogicOperator(Operation):
    """Logic operation combining multiple operations (and, or, not)."""

    operator: LogicOperators
    operations: Sequence[Operation]

    @property
    def operation_type(self) -> Literal[OperationType.LOGIC]:
        return OperationType.LOGIC

    def __post_init__(self) -> None:
        if len(self.operations) == 0:
            raise ValueError("Logic operator requires at least one operation")
