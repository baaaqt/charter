from collections.abc import Sequence
from enum import Enum, StrEnum
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator


class OperationType(Enum):
    """Discriminator for operation types."""

    OPERATOR = "operator"
    LOGIC = "logic"


class Operators(StrEnum):
    EQ = "eq"
    NEQ = "neq"
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


ALL_OPERATORS = {op.value for op in Operators}
ALL_LOGIC_OPERATORS = {op.value for op in LogicOperators}


class ContainsData(BaseModel):
    value: str = Field(min_length=1)
    ignore_case: bool = False


class Operator(BaseModel):
    operator: Operators
    field: str = Field(min_length=1)
    value: Any

    operation_type: Literal[OperationType.OPERATOR] = Field(
        OperationType.OPERATOR, init=False
    )

    @model_validator(mode="after")
    def _validate_value(self) -> Self:
        if self.operator == Operators.IN:
            if isinstance(self.value, str) or not isinstance(self.value, Sequence):
                raise TypeError(
                    f"Operator '{self.operator.value}' requires a sequence value, "
                    f"got {self.value}"
                )
            if len(self.value) == 0:
                raise ValueError(
                    f"Operator '{self.operator.value}' requires a non-empty sequence"
                )

        if self.operator == Operators.CONTAINS and not isinstance(
            self.value, ContainsData
        ):
            if not isinstance(self.value, str):
                raise TypeError(
                    f"Operator '{self.operator.value}' requires a"
                    f" ContainsData or string value, got {self.value}"
                )
            else:
                self.value = ContainsData(value=self.value)

        return self


class LogicOperator(BaseModel):
    operator: LogicOperators
    operations: Sequence["Operation"] = Field(min_length=1)

    operation_type: Literal[OperationType.LOGIC] = Field(
        OperationType.LOGIC, init=False
    )


type Operation = Operator | LogicOperator
