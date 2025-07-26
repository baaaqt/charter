from typing import Any

import pytest

from charter._ops import ContainsData, OperationType, Operator, Operators


class TestOperator:
    def test_init(self) -> None:
        op = Operator(operator=Operators.EQ, field="name", value="test")
        assert op.operator == Operators.EQ
        assert op.field == "name"
        assert op.value == "test"

    @pytest.mark.parametrize("field", ["", None])
    def test_invalid_field(self, field: Any) -> None:
        with pytest.raises(ValueError):
            Operator(operator=Operators.EQ, field=field, value="test")

    @pytest.mark.parametrize("value", [None, 123, [], {}, "value"])
    def test_in_invalid_value(self, value: Any) -> None:
        with pytest.raises(ValueError):
            Operator(operator=Operators.IN, field="tags", value=value)

    @pytest.mark.parametrize("value", ["", None])
    def test_contains_operator_invalid_value(self, value: Any) -> None:
        with pytest.raises(ValueError):
            Operator(operator=Operators.CONTAINS, field="description", value=value)

    def test_operation_type(self) -> None:
        op = Operator(operator=Operators.EQ, field="name", value="test")
        assert op.operation_type == OperationType.OPERATOR


class TestContainsData:
    def test_init(self) -> None:
        data = ContainsData(value="test", ignore_case=True)
        assert data.value == "test"
        assert data.ignore_case is True

    def test_empty_value(self) -> None:
        with pytest.raises(ValueError):
            ContainsData(value="", ignore_case=False)


class TestLogicOperator:
    def test_init(self) -> None:
        from charter._ops import LogicOperator, LogicOperators

        op = LogicOperator(
            operator=LogicOperators.AND,
            operations=[
                Operator(operator=Operators.EQ, field="name", value="test"),
                Operator(operator=Operators.GT, field="age", value=18),
            ],
        )
        assert op.operator == LogicOperators.AND
        assert len(op.operations) == 2

    def test_empty_operations(self) -> None:
        from charter._ops import LogicOperator, LogicOperators

        with pytest.raises(ValueError):
            LogicOperator(operator=LogicOperators.OR, operations=[])

    def test_operation_type(self) -> None:
        from charter._ops import LogicOperator, LogicOperators

        op = LogicOperator(
            operator=LogicOperators.OR,
            operations=[
                Operator(operator=Operators.EQ, field="name", value="test"),
            ],
        )
        assert op.operation_type == OperationType.LOGIC
