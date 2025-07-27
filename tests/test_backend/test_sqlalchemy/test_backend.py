import pytest
import sqlalchemy as sa
from sqlalchemy.dialects import mysql, oracle, postgresql, sqlite
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from charter._backends.sqlalchemy import SQLAlchemyBackend

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
