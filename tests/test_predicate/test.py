"""Tests for the Predicate class."""

import pytest

from charter._ops import (
    ContainsData,
    LogicOperator,
    LogicOperators,
    OperationType,
    Operator,
    Operators,
)
from charter._predicate import Predicate


class TestPredicateBasicOperators:
    def setup_method(self) -> None:
        self.predicate = Predicate()

    def test_eq_operator(self) -> None:
        op = self.predicate.eq("name", "John")

        assert isinstance(op, Operator)
        assert op.operator == Operators.EQ
        assert op.field == "name"
        assert op.value == "John"
        assert op.operation_type == OperationType.OPERATOR

    def test_eq_with_different_types(self) -> None:
        op1 = self.predicate.eq("name", "John")
        assert op1.value == "John"

        op2 = self.predicate.eq("age", 25)
        assert op2.value == 25

        op3 = self.predicate.eq("active", True)
        assert op3.value is True

        op4 = self.predicate.eq("deleted_at", None)
        assert op4.value is None

        op5 = self.predicate.eq("price", 19.99)
        assert op5.value == 19.99

    def test_neq_operator(self) -> None:
        op = self.predicate.neq("name", "John")

        assert isinstance(op, LogicOperator)
        assert op.operator == LogicOperators.NOT
        assert len(op.operations) == 1

        inner_op = op.operations[0]
        assert isinstance(inner_op, Operator)
        assert inner_op.operator == Operators.EQ
        assert inner_op.field == "name"
        assert inner_op.value == "John"

    def test_in_operator(self) -> None:
        values = ["active", "pending", "suspended"]
        op = self.predicate.in_("status", values)

        assert isinstance(op, Operator)
        assert op.operator == Operators.IN
        assert op.field == "status"
        assert op.value == values

    def test_in_operator_with_tuple(self) -> None:
        values = ("admin", "user", "guest")
        op = self.predicate.in_("role", values)

        assert op.value == values

    def test_not_in_operator(self) -> None:
        values = ["banned", "deleted"]
        op = self.predicate.not_in("status", values)

        assert isinstance(op, LogicOperator)
        assert op.operator == LogicOperators.NOT
        assert len(op.operations) == 1

        inner_op = op.operations[0]
        assert isinstance(inner_op, Operator)
        assert inner_op.operator == Operators.IN
        assert inner_op.field == "status"
        assert inner_op.value == values

    def test_gt_operator(self) -> None:
        op = self.predicate.gt("age", 18)

        assert isinstance(op, Operator)
        assert op.operator == Operators.GT
        assert op.field == "age"
        assert op.value == 18

    def test_gte_operator(self) -> None:
        op = self.predicate.gte("age", 21)

        assert isinstance(op, Operator)
        assert op.operator == Operators.GTE
        assert op.field == "age"
        assert op.value == 21

    def test_lt_operator(self) -> None:
        op = self.predicate.lt("age", 65)

        assert isinstance(op, Operator)
        assert op.operator == Operators.LT
        assert op.field == "age"
        assert op.value == 65

    def test_lte_operator(self) -> None:
        op = self.predicate.lte("age", 64)

        assert isinstance(op, Operator)
        assert op.operator == Operators.LTE
        assert op.field == "age"
        assert op.value == 64

    def test_contains_operator_default(self) -> None:
        op = self.predicate.contains("description", "test")

        assert isinstance(op, Operator)
        assert op.operator == Operators.CONTAINS
        assert op.field == "description"
        assert isinstance(op.value, ContainsData)
        assert op.value.value == "test"
        assert op.value.ignore_case is False

    def test_contains_operator_case_insensitive(self) -> None:
        op = self.predicate.contains("description", "TEST", ignore_case=True)

        assert isinstance(op, Operator)
        assert op.operator == Operators.CONTAINS
        assert op.field == "description"
        assert isinstance(op.value, ContainsData)
        assert op.value.value == "TEST"
        assert op.value.ignore_case is True

    def test_regex_operator(self) -> None:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        op = self.predicate.regex("email", pattern)

        assert isinstance(op, Operator)
        assert op.operator == Operators.REGEX
        assert op.field == "email"
        assert op.value == pattern


class TestPredicateLogicOperators:
    def setup_method(self) -> None:
        self.predicate = Predicate()

    def test_and_operator_single(self) -> None:
        op1 = self.predicate.eq("name", "John")
        logic_op = self.predicate.and_(op1)

        assert isinstance(logic_op, LogicOperator)
        assert logic_op.operator == LogicOperators.AND
        assert logic_op.operations == (op1,)
        assert logic_op.operation_type == OperationType.LOGIC

    def test_and_operator_multiple(self) -> None:
        op1 = self.predicate.eq("name", "John")
        op2 = self.predicate.gt("age", 18)
        op3 = self.predicate.eq("active", True)

        logic_op = self.predicate.and_(op1, op2, op3)

        assert isinstance(logic_op, LogicOperator)
        assert logic_op.operator == LogicOperators.AND
        assert logic_op.operations == (op1, op2, op3)
        assert len(logic_op.operations) == 3

    def test_or_operator_single(self) -> None:
        op1 = self.predicate.eq("name", "John")
        logic_op = self.predicate.or_(op1)

        assert isinstance(logic_op, LogicOperator)
        assert logic_op.operator == LogicOperators.OR
        assert logic_op.operations == (op1,)

    def test_or_operator_multiple(self) -> None:
        op1 = self.predicate.eq("name", "John")
        op2 = self.predicate.eq("name", "Jane")
        op3 = self.predicate.eq("name", "Bob")

        logic_op = self.predicate.or_(op1, op2, op3)

        assert isinstance(logic_op, LogicOperator)
        assert logic_op.operator == LogicOperators.OR
        assert logic_op.operations == (op1, op2, op3)
        assert len(logic_op.operations) == 3

    def test_not_operator_single(self) -> None:
        op1 = self.predicate.eq("deleted", True)
        logic_op = self.predicate.not_(op1)

        assert isinstance(logic_op, LogicOperator)
        assert logic_op.operator == LogicOperators.NOT
        assert logic_op.operations == (op1,)
        assert len(logic_op.operations) == 1

    def test_not_operator_multiple(self) -> None:
        op1 = self.predicate.eq("name", "John")
        op2 = self.predicate.gt("age", 18)

        logic_op = self.predicate.not_(op1, op2)

        assert isinstance(logic_op, LogicOperator)
        assert logic_op.operator == LogicOperators.NOT
        assert logic_op.operations == (op1, op2)
        assert len(logic_op.operations) == 2


class TestPredicateComplexQueries:
    def setup_method(self) -> None:
        self.predicate = Predicate()

    def test_nested_logic_operations(self) -> None:
        name_john = self.predicate.eq("name", "John")
        age_gt_18 = self.predicate.gt("age", 18)
        john_condition = self.predicate.and_(name_john, age_gt_18)

        name_jane = self.predicate.eq("name", "Jane")
        active_true = self.predicate.eq("active", True)
        jane_condition = self.predicate.and_(name_jane, active_true)

        final_condition = self.predicate.or_(john_condition, jane_condition)

        assert isinstance(final_condition, LogicOperator)
        assert final_condition.operator == LogicOperators.OR
        assert len(final_condition.operations) == 2

        first_condition = final_condition.operations[0]
        assert isinstance(first_condition, LogicOperator)
        assert first_condition.operator == LogicOperators.AND

        second_condition = final_condition.operations[1]
        assert isinstance(second_condition, LogicOperator)
        assert second_condition.operator == LogicOperators.AND

    def test_complex_not_operations(self) -> None:
        status_in = self.predicate.in_("status", ["banned", "deleted"])
        age_lt_13 = self.predicate.lt("age", 13)
        inner_and = self.predicate.and_(status_in, age_lt_13)
        final_not = self.predicate.not_(inner_and)

        assert isinstance(final_not, LogicOperator)
        assert final_not.operator == LogicOperators.NOT
        assert len(final_not.operations) == 1

        inner_operation = final_not.operations[0]
        assert isinstance(inner_operation, LogicOperator)
        assert inner_operation.operator == LogicOperators.AND

    def test_fluent_api_chaining(self) -> None:
        p = self.predicate

        query = p.or_(
            p.and_(
                p.eq("type", "user"), p.gte("age", 18), p.not_(p.eq("banned", True))
            ),
            p.and_(p.eq("type", "admin"), p.gt("permissions", 5)),
        )

        assert isinstance(query, LogicOperator)
        assert query.operator == LogicOperators.OR
        assert len(query.operations) == 2

    def test_all_operators_in_complex_query(self) -> None:
        p = self.predicate

        query = p.and_(
            p.eq("active", True),
            p.neq("status", "deleted"),
            p.in_("role", ["admin", "moderator"]),
            p.not_in("tags", ["spam", "blocked"]),
            p.gt("age", 18),
            p.gte("score", 100),
            p.lt("warnings", 3),
            p.lte("violations", 0),
            p.contains("bio", "developer", ignore_case=True),
            p.regex("email", r".*@company\.com$"),
        )

        assert isinstance(query, LogicOperator)
        assert query.operator == LogicOperators.AND
        assert len(query.operations) == 10


class TestPredicateEdgeCases:
    def setup_method(self) -> None:
        self.predicate = Predicate()

    def test_empty_string_field_name(self) -> None:
        with pytest.raises(ValueError, match="Field name cannot be empty"):
            self.predicate.eq("", "value")

    def test_whitespace_field_name(self) -> None:
        op = self.predicate.eq("   ", "value")
        assert op.field == "   "
        assert op.value == "value"

    def test_unicode_field_names(self) -> None:
        op = self.predicate.eq("имя_пользователя", "Иван")
        assert op.field == "имя_пользователя"
        assert op.value == "Иван"

    def test_special_characters_in_field_names(self) -> None:
        op1 = self.predicate.eq("user.profile.name", "John")
        assert op1.field == "user.profile.name"

        op2 = self.predicate.eq("user_id", 123)
        assert op2.field == "user_id"

        op3 = self.predicate.eq("first-name", "John")
        assert op3.field == "first-name"

    def test_empty_list_for_in_operator(self) -> None:
        with pytest.raises(ValueError, match="IN operator cannot have empty sequence"):
            self.predicate.in_("status", [])

    def test_non_string_regex_pattern(self) -> None:
        op1 = self.predicate.regex("email", r".*@example\.com")
        assert op1.value == r".*@example\.com"

        op2 = self.predicate.regex(
            "phone", r"^\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$"
        )
        assert "\\d{3}" in op2.value

    def test_contains_with_empty_string(self) -> None:
        with pytest.raises(ValueError, match="Contains value cannot be empty string"):
            self.predicate.contains("description", "")

    def test_large_values(self) -> None:
        large_number = 2**63 - 1
        op = self.predicate.eq("big_number", large_number)
        assert op.value == large_number

        large_string = "x" * 10000
        op2 = self.predicate.contains("text", large_string)
        assert op2.value.value == large_string


class TestPredicateInstantiation:
    def test_predicate_instantiation(self) -> None:
        p = Predicate()
        assert isinstance(p, Predicate)

    def test_predicate_reuse(self) -> None:
        p = Predicate()

        op1 = p.eq("name", "John")
        op2 = p.gt("age", 18)

        assert op1.field == "name"
        assert op2.field == "age"
        assert op1 is not op2

    def test_multiple_predicate_instances(self) -> None:
        p1 = Predicate()
        p2 = Predicate()

        op1 = p1.eq("name", "John")
        op2 = p2.eq("name", "Jane")

        assert op1.value == "John"
        assert op2.value == "Jane"
        assert op1 is not op2

    def test_predicate_has_no_state(self) -> None:
        p = Predicate()

        p.eq("name", "John")
        p.gt("age", 18)

        op = p.eq("status", "active")
        assert op.field == "status"
        assert op.value == "active"
