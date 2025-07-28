from typing import Any

import pytest

from charter._backends.pymongo import PymongoBackend
from charter._exc import UnsupportedOperationError
from charter._ops import ContainsData, Operator, Operators


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
            (Operator(Operators.EQ, "name", "value"), {"name": "value"}),
            (Operator(Operators.IN, "name", ["value"]), {"name": {"$in": ["value"]}}),
            (Operator(Operators.GT, "age", 30), {"age": {"$gt": 30}}),
            (Operator(Operators.GTE, "age", 30), {"age": {"$gte": 30}}),
            (Operator(Operators.LT, "age", 30), {"age": {"$lt": 30}}),
            (Operator(Operators.LTE, "age", 30), {"age": {"$lte": 30}}),
            (
                Operator(
                    Operators.CONTAINS,
                    "name",
                    ContainsData(value="test", ignore_case=False),
                ),
                {"name": {"$regex": "test"}},
            ),
            (
                Operator(
                    Operators.CONTAINS,
                    "name",
                    ContainsData(value="test", ignore_case=True),
                ),
                {"name": {"$regex": "test", "$options": "i"}},
            ),
            (
                Operator(Operators.REGEX, "name", r"^test.*"),
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
        with pytest.raises(
            UnsupportedOperationError,
            match="Unsupported operator: unsupported_operator",
        ):
            self.backend._transform_operator(
                Operator(
                    operator="unsupported_operator",  # type: ignore[arg-type]
                    field="name",
                    value="value",
                )
            )
