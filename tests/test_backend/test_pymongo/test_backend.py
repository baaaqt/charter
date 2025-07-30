from typing import Any
from unittest.mock import Mock

import pytest
from bson import ObjectId

from charter._backends.pymongo import PymongoBackend
from charter._exc import UnsupportedOperationError
from charter._ops import (
    ContainsData,
    LogicOperator,
    LogicOperators,
    Operation,
    Operator,
    Operators,
)


class TestPymongoBackend:
    def setup_method(self) -> None:
        self.backend = PymongoBackend(alias_id=True, convert_id=True)

    def test_transform_empty_operations(self) -> None:
        filters = self.backend.transform([])
        assert filters == []
        assert isinstance(filters, list)

    def test__get_field_name_when_alias_id_true(self) -> None:
        backend = PymongoBackend(alias_id=True, convert_id=False)
        assert backend._get_field_name("id") == "_id"
        assert backend._get_field_name("name") == "name"

    def test__get_field_name_when_alias_id_false(self) -> None:
        backend = PymongoBackend(alias_id=False, convert_id=False)
        assert backend._get_field_name("id") == "id"
        assert backend._get_field_name("name") == "name"

    @pytest.mark.parametrize(
        "operator, expected",
        [
            (
                Operator(operator=Operators.EQ, field="name", value="value"),
                {"name": "value"},
            ),
            (
                Operator(operator=Operators.NEQ, field="name", value="value"),
                {"name": {"$ne": "value"}},
            ),
            (
                Operator(operator=Operators.IN, field="name", value=["value"]),
                {"name": {"$in": ["value"]}},
            ),
            (
                Operator(operator=Operators.GT, field="age", value=30),
                {"age": {"$gt": 30}},
            ),
            (
                Operator(operator=Operators.GTE, field="age", value=30),
                {"age": {"$gte": 30}},
            ),
            (
                Operator(operator=Operators.LT, field="age", value=30),
                {"age": {"$lt": 30}},
            ),
            (
                Operator(operator=Operators.LTE, field="age", value=30),
                {"age": {"$lte": 30}},
            ),
            (
                Operator(
                    operator=Operators.CONTAINS,
                    field="name",
                    value=ContainsData(value="test", ignore_case=False),
                ),
                {"name": {"$regex": "test"}},
            ),
            (
                Operator(
                    operator=Operators.CONTAINS,
                    field="name",
                    value=ContainsData(value="test", ignore_case=True),
                ),
                {"name": {"$regex": "test", "$options": "i"}},
            ),
            (
                Operator(operator=Operators.REGEX, field="name", value=r"^test.*"),
                {"name": {"$regex": r"^test.*"}},
            ),
        ],
    )
    def test__transform_operator(
        self,
        operator: Operator,
        expected: dict[str, Any],
    ) -> None:
        transformed = self.backend._transform_operator(operator)
        assert transformed == expected

    def test__transform_operator_invalid_operator(self) -> None:
        mock = Mock(spec=Operator)
        mock.operator = "unsupported_operator"
        mock.field = "name"

        with pytest.raises(
            UnsupportedOperationError,
            match="Unsupported operator: unsupported_operator",
        ):
            self.backend._transform_operator(mock)

    def test__transform_operator_with_id_conversion(self) -> None:
        backend = PymongoBackend(alias_id=True, convert_id=True)
        operator = Operator(
            operator=Operators.EQ,
            field="id",
            value="6887106233516d43a9c29753",
        )
        transformed = backend._transform_operator(operator)
        assert isinstance(transformed["_id"], ObjectId)
        assert transformed["_id"] == ObjectId("6887106233516d43a9c29753")

    def test__transform_operator_with_id_conversion_in_list(self) -> None:
        backend = PymongoBackend(alias_id=True, convert_id=True)
        operator = Operator(
            operator=Operators.IN,
            field="id",
            value=["6887106233516d43a9c29753"],
        )
        transformed = backend._transform_operator(operator)
        assert isinstance(transformed["_id"]["$in"][0], ObjectId)
        assert transformed["_id"]["$in"][0] == ObjectId("6887106233516d43a9c29753")

    @pytest.mark.parametrize(
        "operator, expected",
        [
            (
                LogicOperator(
                    operator=LogicOperators.AND,
                    operations=[
                        Operator(operator=Operators.EQ, field="name", value="test"),
                        Operator(operator=Operators.GT, field="age", value=20),
                    ],
                ),
                {"$and": [{"name": "test"}, {"age": {"$gt": 20}}]},
            ),
            (
                LogicOperator(
                    operator=LogicOperators.OR,
                    operations=[
                        Operator(operator=Operators.EQ, field="name", value="test"),
                        Operator(operator=Operators.LT, field="age", value=30),
                    ],
                ),
                {"$or": [{"name": "test"}, {"age": {"$lt": 30}}]},
            ),
            (
                LogicOperator(
                    operator=LogicOperators.NOT,
                    operations=[
                        Operator(
                            operator=Operators.EQ,
                            field="name",
                            value="test",
                        )
                    ],
                ),
                {"$not": [{"name": "test"}]},
            ),
        ],
    )
    def test__transform_logic_operator(
        self,
        operator: LogicOperator,
        expected: dict[str, Any],
    ) -> None:
        transformed = self.backend._transform_logic_operator(operator)
        assert transformed == expected

    def test__transform_logic_operator_invalid_operator(self) -> None:
        mock = Mock(spec=LogicOperator)
        mock.operations = [
            Operator(operator=Operators.EQ, field="name", value="test"),
        ]
        mock.operator = "unsupported_operator"
        with pytest.raises(
            UnsupportedOperationError,
            match="Unsupported logic operator: unsupported_operator",
        ):
            self.backend._transform_logic_operator(mock)

    def test_transform_unsupported_operation_type(self) -> None:
        mock = Mock(spec=Operator)
        mock.operation_type = "unsupported_operation"

        with pytest.raises(
            UnsupportedOperationError,
            match="Unsupported operation type: unsupported_operation",
        ):
            self.backend.transform([mock])

    @pytest.mark.parametrize(
        "operations, expected",
        [
            (
                [
                    Operator(operator=Operators.EQ, field="name", value="test"),
                    LogicOperator(
                        operator=LogicOperators.AND,
                        operations=[
                            Operator(operator=Operators.GT, field="age", value=20),
                            Operator(operator=Operators.LT, field="age", value=30),
                        ],
                    ),
                ],
                [
                    {"name": "test"},
                    {"$and": [{"age": {"$gt": 20}}, {"age": {"$lt": 30}}]},
                ],
            ),
            (
                [
                    LogicOperator(
                        operator=LogicOperators.OR,
                        operations=[
                            Operator(operator=Operators.EQ, field="name", value="test"),
                            Operator(
                                operator=Operators.IN,
                                field="tags",
                                value=["tag1", "tag2"],
                            ),
                        ],
                    )
                ],
                [{"$or": [{"name": "test"}, {"tags": {"$in": ["tag1", "tag2"]}}]}],
            ),
            (
                [
                    LogicOperator(
                        operator=LogicOperators.NOT,
                        operations=[
                            Operator(operator=Operators.EQ, field="name", value="test")
                        ],
                    ),
                    LogicOperator(
                        operator=LogicOperators.AND,
                        operations=[
                            Operator(operator=Operators.GT, field="age", value=20),
                            Operator(operator=Operators.LT, field="age", value=30),
                        ],
                    ),
                    LogicOperator(
                        operator=LogicOperators.OR,
                        operations=[
                            Operator(
                                operator=Operators.EQ, field="status", value="active"
                            ),
                            Operator(
                                operator=Operators.IN,
                                field="tags",
                                value=["tag1", "tag2"],
                            ),
                            LogicOperator(
                                operator=LogicOperators.NOT,
                                operations=[
                                    Operator(
                                        operator=Operators.EQ,
                                        field="name",
                                        value="test",
                                    )
                                ],
                            ),
                            LogicOperator(
                                operator=LogicOperators.AND,
                                operations=[
                                    Operator(
                                        operator=Operators.GT,
                                        field="age",
                                        value=20,
                                    ),
                                    Operator(
                                        operator=Operators.LT,
                                        field="age",
                                        value=30,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                [
                    {"$not": [{"name": "test"}]},
                    {"$and": [{"age": {"$gt": 20}}, {"age": {"$lt": 30}}]},
                    {
                        "$or": [
                            {"status": "active"},
                            {"tags": {"$in": ["tag1", "tag2"]}},
                            {"$not": [{"name": "test"}]},
                            {"$and": [{"age": {"$gt": 20}}, {"age": {"$lt": 30}}]},
                        ]
                    },
                ],
            ),
        ],
    )
    def test_transform_edge_cases(
        self,
        operations: list[Operation],
        expected: list[dict[str, Any]],
    ) -> None:
        result = self.backend.transform(operations)
        assert result == expected
        assert isinstance(result, list)
