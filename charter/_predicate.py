from collections.abc import Sequence
from typing import Any

from charter._ops import (
    ContainsData,
    LogicOperator,
    LogicOperators,
    Operation,
    Operator,
    Operators,
)


class Predicate:
    def or_(self, *operations: Operation) -> LogicOperator:
        return LogicOperator(operator=LogicOperators.OR, operations=operations)

    def and_(self, *operations: Operation) -> LogicOperator:
        return LogicOperator(operator=LogicOperators.AND, operations=operations)

    def not_(self, *operations: Operation) -> LogicOperator:
        return LogicOperator(operator=LogicOperators.NOT, operations=operations)

    def eq(self, field: str, value: Any) -> Operator:
        return Operator(operator=Operators.EQ, field=field, value=value)

    def neq(self, field: str, value: Any) -> Operator:
        return Operator(Operators.NEQ, field, value)

    def in_(self, field: str, values: Sequence[Any]) -> Operator:
        return Operator(operator=Operators.IN, field=field, value=values)

    def not_in(self, field: str, values: Sequence[Any]) -> LogicOperator:
        return self.not_(self.in_(field, values))

    def gt(self, field: str, value: Any) -> Operator:
        return Operator(operator=Operators.GT, field=field, value=value)

    def gte(self, field: str, value: Any) -> Operator:
        return Operator(operator=Operators.GTE, field=field, value=value)

    def lt(self, field: str, value: Any) -> Operator:
        return Operator(operator=Operators.LT, field=field, value=value)

    def lte(self, field: str, value: Any) -> Operator:
        return Operator(operator=Operators.LTE, field=field, value=value)

    def contains(self, field: str, value: str, ignore_case: bool = False) -> Operator:
        return Operator(
            operator=Operators.CONTAINS,
            field=field,
            value=ContainsData(value=value, ignore_case=ignore_case),
        )

    def regex(self, field: str, pattern: str) -> Operator:
        return Operator(operator=Operators.REGEX, field=field, value=pattern)
