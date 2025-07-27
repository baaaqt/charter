import pytest
import sqlalchemy as sa
from sqlalchemy.dialects import mysql, oracle, postgresql, sqlite
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from charter._backends.sqlalchemy import SQLAlchemyBackend
from charter._ops import (
    ContainsData,
    LogicOperator,
    LogicOperators,
    Operator,
    Operators,
)

DIALECT_MAPPING = {
    "postgresql": postgresql.dialect(),
    "mysql": mysql.dialect(),
    "sqlite": sqlite.dialect(),
    "oracle": oracle.dialect(),
}


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int]
    role: Mapped[str]


class TestSQLAlchemyBackend:
    def setup_method(self) -> None:
        self.backend = SQLAlchemyBackend(User)

    def test_transform_empty_operations(self) -> None:
        filters = self.backend.transform([])
        assert filters is sa.true()
        assert (
            str(
                filters.compile(
                    dialect=postgresql.dialect(),
                    compile_kwargs={"literal_binds": True},
                )
            )
            == "true"
        )

    @pytest.mark.parametrize(
        "field_name",
        ["name", "age", "id", "role"],
    )
    def test__get_column(self, field_name: str) -> None:
        column = self.backend._get_column(field_name)
        assert isinstance(column, sa.Column)
        assert column.name == field_name

    @pytest.mark.parametrize(
        "dialect",
        [
            "postgresql",
            "mysql",
            "oracle",
            "sqlite",
        ],
    )
    def test__transform_regex(self, dialect: str) -> None:
        result = self.backend._transform_regex(
            self.backend._get_column("name"), r"^test.*"
        )
        compiled = str(
            result.compile(
                dialect=DIALECT_MAPPING[dialect],
                compile_kwargs={"literal_binds": True},
            )
        )
        assert compiled == "users.name REGEXP '^test.*'"

    @pytest.mark.parametrize(
        "dialect, expected",
        [
            ["postgresql", "users.name LIKE '%%test%%'"],
            ["mysql", "users.name LIKE '%%test%%'"],
            ["oracle", "users.name LIKE '%test%'"],
            ["sqlite", "users.name LIKE '%test%'"],
        ],
    )
    def test__transform_contains_case_sensitive(
        self,
        dialect: str,
        expected: str,
    ) -> None:
        contains_data = ContainsData(value="test", ignore_case=False)
        result = self.backend._transform_contains(
            self.backend._get_column("name"), contains_data
        )
        compiled = str(
            result.compile(
                dialect=DIALECT_MAPPING[dialect],
                compile_kwargs={"literal_binds": True},
            )
        )
        assert compiled == expected

    @pytest.mark.parametrize(
        "dialect, expected",
        [
            ["postgresql", "lower(users.name) like '%%test%%'"],
            ["mysql", "lower(users.name) like '%%test%%'"],
            ["oracle", "lower(users.name) like '%test%'"],
            ["sqlite", "lower(users.name) like '%test%'"],
        ],
    )
    def test__transform_contains_case_insensitive_with_lower_like(
        self,
        dialect: str,
        expected: str,
    ) -> None:
        backend = SQLAlchemyBackend(User, use_lower_like=True)
        contains_data = ContainsData(value="TEST", ignore_case=True)
        result = backend._transform_contains(backend._get_column("name"), contains_data)
        compiled = str(
            result.compile(
                dialect=DIALECT_MAPPING[dialect],
                compile_kwargs={"literal_binds": True},
            )
        ).lower()
        assert compiled == expected

    @pytest.mark.parametrize(
        "dialect, expected",
        [
            ["postgresql", "users.name ilike '%%test%%'"],
            ["mysql", "lower(users.name) like lower('%%test%%')"],
            ["oracle", "lower(users.name) like lower('%test%')"],
            ["sqlite", "lower(users.name) like lower('%test%')"],
        ],
    )
    def test__transform_contains_case_insensitive_with_ilike(
        self,
        dialect: str,
        expected: str,
    ) -> None:
        backend = SQLAlchemyBackend(User, use_lower_like=False)
        contains_data = ContainsData(value="TEST", ignore_case=True)
        result = backend._transform_contains(backend._get_column("name"), contains_data)
        compiled = str(
            result.compile(
                dialect=DIALECT_MAPPING[dialect],
                compile_kwargs={"literal_binds": True},
            )
        ).lower()
        assert compiled == expected

    @pytest.mark.parametrize(
        "operator, expected",
        [
            (
                Operator(field="name", operator=Operators.EQ, value="test"),
                "users.name = 'test'",
            ),
            (
                Operator(field="name", operator=Operators.EQ, value=None),
                "users.name IS NULL",
            ),
            (
                Operator(field="name", operator=Operators.EQ, value=True),
                "users.name IS true",
            ),
            (
                Operator(field="name", operator=Operators.EQ, value=False),
                "users.name IS false",
            ),
            (
                Operator(field="age", operator=Operators.IN, value=[20, 30]),
                "users.age IN (20, 30)",
            ),
            (
                Operator(field="age", operator=Operators.GT, value=25),
                "users.age > 25",
            ),
            (
                Operator(field="age", operator=Operators.GTE, value=30),
                "users.age >= 30",
            ),
            (
                Operator(field="age", operator=Operators.LT, value=40),
                "users.age < 40",
            ),
            (
                Operator(field="age", operator=Operators.LTE, value=50),
                "users.age <= 50",
            ),
            (
                Operator(
                    field="name",
                    operator=Operators.CONTAINS,
                    value=ContainsData(value="test", ignore_case=False),
                ),
                "users.name LIKE '%%test%%'",
            ),
            (
                Operator(
                    field="name",
                    operator=Operators.REGEX,
                    value=r"^test.*",
                ),
                "users.name REGEXP '^test.*'",
            ),
        ],
    )
    def test__transform_operator(
        self,
        operator: Operator,
        expected: str,
    ) -> None:
        result = self.backend._transform_operator(operator)
        compiled = str(
            result.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True},
            )
        )
        assert compiled == expected

    @pytest.mark.parametrize(
        "operator, expected",
        [
            [
                LogicOperator(
                    operator=LogicOperators.AND,
                    operations=[
                        Operator(field="name", operator=Operators.EQ, value="test"),
                        Operator(field="age", operator=Operators.GT, value=20),
                    ],
                ),
                "users.name = 'test' AND users.age > 20",
            ],
            [
                LogicOperator(
                    operator=LogicOperators.OR,
                    operations=[
                        Operator(field="name", operator=Operators.EQ, value="test"),
                        Operator(field="age", operator=Operators.GT, value=20),
                    ],
                ),
                "users.name = 'test' OR users.age > 20",
            ],
            [
                LogicOperator(
                    operator=LogicOperators.NOT,
                    operations=[
                        Operator(field="name", operator=Operators.EQ, value="test"),
                    ],
                ),
                "users.name != 'test'",
            ],
            [
                LogicOperator(
                    operator=LogicOperators.NOT,
                    operations=[
                        Operator(field="name", operator=Operators.IN, value=["name"]),
                    ],
                ),
                "(users.name NOT IN ('name'))",
            ],
            [
                LogicOperator(
                    operator=LogicOperators.NOT,
                    operations=[
                        Operator(field="name", operator=Operators.EQ, value="test"),
                        LogicOperator(
                            operator=LogicOperators.OR,
                            operations=[
                                Operator(field="age", operator=Operators.GT, value=20),
                                Operator(
                                    field="role", operator=Operators.EQ, value="admin"
                                ),
                            ],
                        ),
                    ],
                ),
                "NOT (users.name = 'test' AND"
                " (users.age > 20 OR users.role = 'admin'))",
            ],
        ],
    )
    def test__transform_logic_operator(
        self, operator: LogicOperator, expected: str
    ) -> None:
        result = self.backend._transform_logic_operator(operator)
        compiled = str(
            result.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True},
            )
        )
        assert compiled == expected
