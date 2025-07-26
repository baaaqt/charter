from unittest.mock import Mock

import pytest
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from charter._backends.sqlalchemy import SQLAlchemyBackend
from charter._exc import UnsupportedOperationError
from charter._ops import LogicOperator, Operator
from charter._predicate import Predicate


class TestSQLAlchemyBackendErrors:
    class Base(DeclarativeBase):
        """Base class for SQLAlchemy models."""

    class User(Base):
        """User model for testing."""

        __tablename__ = "users"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str]
        age: Mapped[int]
        role: Mapped[str]

    def setup_method(self) -> None:
        self.backend = SQLAlchemyBackend(TestSQLAlchemyBackendErrors.User)

    def test_entity_not_declarative_base(
        self,
        backend: type[SQLAlchemyBackend],
    ) -> None:
        with pytest.raises(
            TypeError,
            match="Entity must be a subclass of DeclarativeBase",
        ):
            backend(object)  # type: ignore[arg-type]

    def test_transform_invalid_operation_type(self) -> None:
        mock = Mock(spec=Operator)
        mock.operation_type = "invalid"

        with pytest.raises(
            UnsupportedOperationError,
            match="Unsupported operation type: invalid",
        ):
            self.backend.transform([mock])

    def test__transform_logic_operator_invalid_logic_operator(self) -> None:
        with pytest.raises(
            UnsupportedOperationError,
            match="Unsupported logic operator: invalid",
        ):
            self.backend._transform_logic_operator(
                LogicOperator(
                    operator="invalid",  # type: ignore[arg-type]
                    operations=[Predicate().eq("name", "test")],
                )
            )

    def test__transform_operation_with_invalid_field(self) -> None:
        with pytest.raises(
            ValueError,
            match="Field 'invalid_field' not found in entity",
        ):
            self.backend.transform(
                [
                    Operator(
                        operator="eeq",  # type: ignore[arg-type]
                        field="invalid_field",
                        value="test",
                    ),
                ]
            )
