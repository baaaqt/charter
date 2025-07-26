from typing import cast

from charter._ops import (
    LogicOperator,
    LogicOperators,
    OperationType,
    Operator,
    Operators,
)
from charter._predicate import Predicate


def test_predicate_demo_usage() -> None:
    p = Predicate()

    name_is_john = p.eq("name", "John")
    age_over_18 = p.gt("age", 18)
    status_active = p.in_("status", ["active", "verified"])

    assert name_is_john.operator == Operators.EQ
    assert name_is_john.field == "name"
    assert name_is_john.value == "John"

    assert age_over_18.operator == Operators.GT
    assert age_over_18.field == "age"
    assert age_over_18.value == 18

    adult_john = p.and_(name_is_john, age_over_18)
    eligible_user = p.and_(adult_john, status_active)

    assert adult_john.operator == LogicOperators.AND
    assert len(adult_john.operations) == 2

    assert eligible_user.operation_type == OperationType.LOGIC
    assert eligible_user.operator == LogicOperators.AND


def test_predicate_fluent_api_demo() -> None:
    p = Predicate()

    query = p.or_(
        p.and_(p.eq("role", "admin"), p.eq("active", True)),
        p.and_(
            p.eq("role", "user"),
            p.gte("age", 21),
            p.eq("subscription", "premium"),
            p.not_(p.eq("banned", True)),
        ),
    )

    assert query.operator == LogicOperators.OR
    assert len(query.operations) == 2

    admin_branch = cast(LogicOperator, query.operations[0])
    assert admin_branch.operator == LogicOperators.AND
    assert len(admin_branch.operations) == 2

    user_branch = cast(LogicOperator, query.operations[1])
    assert user_branch.operator == LogicOperators.AND
    assert len(user_branch.operations) == 4


def test_all_operators_integration() -> None:
    p = Predicate()

    operations = [
        p.eq("name", "John"),
        p.neq("status", "deleted"),
        p.in_("role", ["admin", "user"]),
        p.not_in("tags", ["spam"]),
        p.gt("age", 18),
        p.gte("score", 100),
        p.lt("violations", 3),
        p.lte("warnings", 2),
        p.contains("bio", "developer"),
        p.regex("email", r".*@company\.com$"),
    ]

    all_conditions = p.and_(*operations)

    assert all_conditions.operator == LogicOperators.AND
    assert len(all_conditions.operations) == 10

    operator_types = set()
    for op in all_conditions.operations:
        if isinstance(op, Operator):
            operator_types.add(op.operator)
        elif isinstance(op, LogicOperator):
            for nested_op in op.operations:
                if isinstance(nested_op, Operator):
                    operator_types.add(nested_op.operator)

    expected_basic_ops = {
        Operators.EQ,
        Operators.IN,
        Operators.GT,
        Operators.GTE,
        Operators.LT,
        Operators.LTE,
        Operators.CONTAINS,
        Operators.REGEX,
    }

    assert len(operator_types.intersection(expected_basic_ops)) >= 6


if __name__ == "__main__":
    print("🧪 Running Predicate Demo Tests...")

    test_predicate_demo_usage()
    print("✅ Basic usage demo passed")

    test_predicate_fluent_api_demo()
    print("✅ Fluent API demo passed")

    test_all_operators_integration()
    print("✅ All operators integration test passed")

    print("\n🎉 All demo tests passed! The Predicate class is working correctly.")
