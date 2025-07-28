from collections.abc import Sequence
from typing import Any, cast

from bson import ObjectId

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


class PymongoBackend(Backend[list[dict[str, Any]]]):
    """Backend for Beanie/MongoDB queries.

    Transforms operations into MongoDB query dictionaries.
    """

    def __init__(self, alias_id: bool = False, convert_id: bool = False) -> None:
        """Initialize Beanie backend.

        Args:
            alias_id: Whether to convert 'id' field to '_id' for MongoDB
            convert_id: Whether to convert 'id' field to ObjectId for MongoDB
        """
        self.alias_id = alias_id
        self.convert_id = convert_id

    def transform(self, operations: Sequence[Operation]) -> list[dict[str, Any]]:
        criteria: list[dict[str, Any]] = []
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

        return criteria

    def _transform_logic_operator(self, op: LogicOperator) -> dict[str, Any]:
        transformed_ops = self.transform(op.operations)

        match op.operator:
            case LogicOperators.AND:
                return {"$and": transformed_ops}
            case LogicOperators.OR:
                return {"$or": transformed_ops}
            case LogicOperators.NOT:
                return {"$not": transformed_ops}
            case _:
                raise UnsupportedOperationError(
                    f"Unsupported logic operator: {op.operator}"
                )

    def _transform_operator(self, op: Operator) -> dict[str, Any]:
        field = self._get_field_name(op.field)
        if self.convert_id and field == "_id":
            if op.operator == Operators.IN:
                op = Operator(
                    operator=op.operator,
                    field=field,
                    value=[ObjectId(v) for v in op.value],
                )
            else:
                op = Operator(
                    operator=op.operator,
                    field=field,
                    value=ObjectId(op.value),
                )

        match op.operator:
            case Operators.EQ:
                return {field: op.value}
            case Operators.NEQ:
                return {field: {"$ne": op.value}}
            case Operators.IN:
                return {field: {"$in": op.value}}
            case Operators.GT:
                return {field: {"$gt": op.value}}
            case Operators.GTE:
                return {field: {"$gte": op.value}}
            case Operators.LT:
                return {field: {"$lt": op.value}}
            case Operators.LTE:
                return {field: {"$lte": op.value}}
            case Operators.CONTAINS:
                return self._transform_contains(field, cast(ContainsData, op.value))
            case Operators.REGEX:
                return {field: {"$regex": op.value}}
            case _:
                raise UnsupportedOperationError(f"Unsupported operator: {op.operator}")

    def _transform_contains(
        self,
        field: str,
        contains_data: ContainsData,
    ) -> dict[str, Any]:
        if contains_data.ignore_case:
            return {field: {"$regex": contains_data.value.lower(), "$options": "i"}}
        return {field: {"$regex": contains_data.value}}

    def _get_field_name(self, field: str) -> str:
        if self.alias_id and field == "id":
            return "_id"
        return field
