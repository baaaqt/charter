from unittest.mock import Mock

import pytest
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from charter._backends.sqlalchemy import SQLAlchemyBackend
from charter._exc import UnsupportedOperationError
from charter._ops import Operator


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

    def test_entity_not_declarative_base(self) -> None:
        with pytest.raises(
            TypeError,
            match="Entity must be a subclass of DeclarativeBase",
        ):
            SQLAlchemyBackend(object)  # type: ignore[arg-type]

    def test_transform_invalid_operation_type(self) -> None:
        mock = Mock(spec=Operator)
        mock.operation_type = "invalid"

        with pytest.raises(
            UnsupportedOperationError,
            match="Unsupported operation type: invalid",
        ):
            self.backend.transform([mock])

    def test__transform_logic_operator_invalid_logic_operator(self) -> None:
        mock = Mock(spec=Operator)
        mock.operator = "invalid"
        with pytest.raises(
            UnsupportedOperationError,
            match="Unsupported logic operator: invalid",
        ):
            self.backend._transform_logic_operator(mock)

    def test__transform_operator_invalid_operator(self) -> None:
        mock = Mock(spec=Operator)
        mock.operator = "invalid"
        mock.field = "name"
        with pytest.raises(
            UnsupportedOperationError,
            match="Unsupported operator: invalid",
        ):
            self.backend._transform_operator(mock)

    def test__get_column_with_non_existing_column(self) -> None:
        with pytest.raises(
            AttributeError,
            match=f"Object of type {self.User.__class__}"
            " has no attribute 'invalid_field'",
        ):
            self.backend.transform(
                [
                    Operator(
                        operator="eq",  # type: ignore[arg-type]
                        field="invalid_field",
                        value="test",
                    ),
                ]
            )
