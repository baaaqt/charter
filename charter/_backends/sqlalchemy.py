from collections.abc import Callable, Sequence
from typing import Any, cast

import sqlalchemy as sa
from sqlalchemy import Column, ColumnElement, func
from sqlalchemy.orm import DeclarativeBase

from charter._backends.interface import Backend
from charter._exc import UnsupportedOperationError
from charter._ops import (
    ContainsData,
    LogicOperator,
    LogicOperators,
    Operation,
    OperationType,
    Operator,
    Operators,
)


class SQLAlchemyBackend(Backend[ColumnElement[bool]]):
    """
    Backend for SQLAlchemy ORM queries.

    Transforms operations into SQLAlchemy column expressions.
    """

    entity: type[DeclarativeBase]
    generate_contains_ignore_case: Callable[
        [ColumnElement[Any], str], ColumnElement[bool]
    ]

    def __init__(
        self,
        entity: type[DeclarativeBase],
        *,
        use_lower_like: bool = False,
    ) -> None:
        """Initialize SQLAlchemy backend.

        Args:
            entity: SQLAlchemy model class
        """
        if not issubclass(entity, DeclarativeBase):
            raise TypeError(
                f"Entity must be a subclass of DeclarativeBase, got {entity}"
            )

        self.entity = entity

        if use_lower_like:
            self.generate_contains_ignore_case = lambda c, p: func.lower(c).like(
                p.lower()
            )
        else:
            self.generate_contains_ignore_case = lambda c, p: c.ilike(p.lower())

    def transform(self, operations: Sequence[Operation]) -> ColumnElement[bool]:
        if not operations:
            return sa.true()

        criteria: list[ColumnElement[bool]] = []

        for op in operations:
            match op.operation_type:
                case OperationType.OPERATOR:
                    criteria.append(self._transform_operator(cast(Operator, op)))
                case OperationType.LOGIC:
                    criteria.append(
                        self._transform_logic_operator(cast(LogicOperator, op))
                    )
                case _:
                    raise UnsupportedOperationError(
                        f"Unsupported operation type: {op.operation_type}"
                    )

        if len(criteria) == 1:
            return criteria[0]

        return sa.and_(*criteria)

    def _transform_logic_operator(self, op: LogicOperator) -> ColumnElement[bool]:
        match op.operator:
            case LogicOperators.AND:
                return sa.and_(*self.transform(op.operations))
            case LogicOperators.OR:
                return sa.or_(*self.transform(op.operations))
            case LogicOperators.NOT:
                return ~self.transform(op.operations)
            case _:
                raise UnsupportedOperationError(
                    f"Unsupported logic operator: {op.operator}"
                )

    def _transform_operator(self, op: Operator) -> ColumnElement[bool]:
        column = self._get_column(op.field)
        match op.operator:
            case Operators.EQ:
                match op.value:
                    case None:
                        return column.is_(None)
                    case bool():
                        return column.is_(op.value)
                    case _:
                        return column == op.value  # type: ignore[no-any-return]

            case Operators.NEQ:
                match op.value:
                    case None:
                        return column.isnot(None)
                    case bool():
                        return column.isnot(op.value)
                    case _:
                        return column != op.value  # type: ignore[no-any-return]

            case Operators.IN:
                return column.in_(op.value)
            case Operators.GT:
                return column > op.value  # type: ignore[no-any-return]
            case Operators.GTE:
                return column >= op.value  # type: ignore[no-any-return]
            case Operators.LT:
                return column < op.value  # type: ignore[no-any-return]
            case Operators.LTE:
                return column <= op.value  # type: ignore[no-any-return]
            case Operators.CONTAINS:
                return self._transform_contains(column, cast(ContainsData, op.value))
            case Operators.REGEX:
                return self._transform_regex(column, op.value)
            case _:
                raise UnsupportedOperationError(f"Unsupported operator: {op.operator}")

    def _transform_contains(
        self,
        column: ColumnElement[Any],
        contains_data: ContainsData,
    ) -> ColumnElement[bool]:
        pattern = f"%{contains_data.value}%"

        if contains_data.ignore_case:
            return self.generate_contains_ignore_case(column, pattern)
        return column.like(pattern)

    def _transform_regex(
        self,
        column: ColumnElement[Any],
        pattern: str,
    ) -> ColumnElement[bool]:
        """Transform regex operation to SQLAlchemy regex operator."""
        # Note: REGEXP operator may not be available in all databases
        # PostgreSQL uses ~, MySQL uses REGEXP, SQLite uses REGEXP (with extension)
        return column.op("REGEXP")(pattern)

    def _get_column(self, field_name: str) -> Column[Any]:
        """Get column attribute from entity."""
        column = self.entity.__mapper__.columns.get(field_name)

        if column is None:
            raise AttributeError(
                f"Object of type {self.entity.__class__}"
                f" has no attribute '{field_name}'"
            )
        return column
