"""Performance and stress tests for the Predicate class."""

import time

import pytest

from charter._ops import LogicOperator, Operator
from charter._predicate import Predicate


class TestPredicatePerformance:
    def setup_method(self) -> None:
        self.predicate = Predicate()

    def test_large_number_of_operations(self) -> None:
        start_time = time.time()

        operations = []
        for i in range(1000):
            op = self.predicate.eq(f"field_{i}", f"value_{i}")
            operations.append(op)

        end_time = time.time()
        execution_time = end_time - start_time

        assert execution_time < 1.0
        assert len(operations) == 1000

        for i, op in enumerate(operations):
            assert op.field == f"field_{i}"
            assert op.value == f"value_{i}"

    def test_deeply_nested_logic_operations(self) -> None:
        start_time = time.time()

        base_op = self.predicate.eq("base", "value")
        current_op: Operator | LogicOperator = base_op

        for i in range(100):
            current_op = self.predicate.and_(
                current_op, self.predicate.eq(f"field_{i}", i)
            )

        end_time = time.time()
        execution_time = end_time - start_time

        assert execution_time < 1.0
        assert isinstance(current_op, LogicOperator)

    def test_large_in_operator_values(self) -> None:
        large_list = list(range(10000))

        start_time = time.time()
        op = self.predicate.in_("id", large_list)
        end_time = time.time()

        execution_time = end_time - start_time
        assert execution_time < 0.1
        assert len(op.value) == 10000

    def test_complex_query_building(self) -> None:
        start_time = time.time()

        p = self.predicate
        query = p.and_(
            p.or_(
                p.eq("role", "admin"),
                p.and_(p.eq("role", "user"), p.gte("reputation", 1000)),
            ),
            p.not_(p.eq("banned", True)),
            p.in_("status", ["active", "verified", "premium"]),
            p.or_(p.lte("age", 65), p.eq("senior_account", True)),
            p.contains("bio", "developer", ignore_case=True),
            p.regex("email", r".*@(company|enterprise)\.com$"),
        )

        end_time = time.time()
        execution_time = end_time - start_time

        assert execution_time < 0.01
        assert isinstance(query, LogicOperator)

    @pytest.mark.parametrize("operation_count", [10, 100, 500])
    def test_and_operation_scalability(self, operation_count: int) -> None:
        operations = [
            self.predicate.eq(f"field_{i}", f"value_{i}")
            for i in range(operation_count)
        ]

        start_time = time.time()
        result = self.predicate.and_(*operations)
        end_time = time.time()

        execution_time = end_time - start_time
        assert execution_time < 0.1
        assert len(result.operations) == operation_count

    @pytest.mark.parametrize("operation_count", [10, 100, 500])
    def test_or_operation_scalability(self, operation_count: int) -> None:
        operations = [
            self.predicate.eq("status", f"status_{i}") for i in range(operation_count)
        ]

        start_time = time.time()
        result = self.predicate.or_(*operations)
        end_time = time.time()

        execution_time = end_time - start_time
        assert execution_time < 0.1
        assert len(result.operations) == operation_count


class TestPredicateStressTests:
    def setup_method(self) -> None:
        self.predicate = Predicate()

    def test_memory_usage_with_many_operations(self) -> None:
        import gc

        gc.collect()
        initial_objects = len(gc.get_objects())

        operations = []
        for i in range(1000):
            op = self.predicate.eq(f"field_{i}", f"value_{i}")
            operations.append(op)

        gc.collect()
        final_objects = len(gc.get_objects())

        object_growth = final_objects - initial_objects
        assert object_growth < 5000

    def test_unicode_heavy_operations(self) -> None:
        unicode_strings = [
            "🚀 测试中文字符",
            "Тест на русском языке",
            "اختبار باللغة العربية",
            "🎯 Ελληνικά χαρακτήρες",
            "日本語のテスト文字列",
        ]

        operations = []
        for i, unicode_str in enumerate(unicode_strings):
            op = self.predicate.contains(
                f"description_{i}", unicode_str, ignore_case=True
            )
            operations.append(op)

            assert op.value.value == unicode_str

        combined = self.predicate.and_(*operations)
        assert len(combined.operations) == len(unicode_strings)

    def test_very_long_field_names(self) -> None:
        long_field_name = "a" * 1000
        op = self.predicate.eq(long_field_name, "value")

        assert op.field == long_field_name
        assert len(op.field) == 1000

    def test_very_long_values(self) -> None:
        long_value = "x" * 10000
        op = self.predicate.eq("field", long_value)

        assert op.value == long_value
        assert len(op.value) == 10000

    def test_empty_operations_handling(self) -> None:
        test_cases = [
            ("field", ""),
            ("field", 0),
            ("field", False),
            ("field", []),
            ("field", None),
        ]

        for field, value in test_cases:
            if field == "field" and value == []:
                with pytest.raises(ValueError):
                    self.predicate.in_(field, value)  # type: ignore[arg-type]
            else:
                op = self.predicate.eq(field, value)
                assert op.field == field
                assert op.value == value

    def test_rapid_fire_operations(self) -> None:
        operations = []

        start_time = time.time()
        for i in range(10000):
            op = self.predicate.eq("rapid_field", i)
            operations.append(op)
        end_time = time.time()

        execution_time = end_time - start_time
        assert execution_time < 1.0
        assert len(operations) == 10000

        assert operations[0].value == 0
        assert operations[9999].value == 9999


class TestPredicateRealWorldScenarios:
    def setup_method(self) -> None:
        self.predicate = Predicate()

    def test_user_search_query(self) -> None:
        p = self.predicate

        query = p.and_(
            p.eq("active", True),
            p.neq("deleted_at", None),
            p.or_(p.eq("role", "admin"), p.gte("reputation", 1000)),
            p.in_("subscription_type", ["premium", "enterprise"]),
            p.contains("bio", "python", ignore_case=True),
        )

        assert isinstance(query, LogicOperator)
        assert len(query.operations) == 5

    def test_e_commerce_product_filter(self) -> None:
        p = self.predicate

        query = p.and_(
            p.eq("category", "electronics"),
            p.gte("price", 100),
            p.lte("price", 500),
            p.gt("stock_quantity", 0),
            p.gte("average_rating", 4.0),
            p.not_(p.eq("discontinued", True)),
            p.or_(
                p.contains("name", "laptop", ignore_case=True),
                p.contains("name", "phone", ignore_case=True),
                p.contains("description", "gaming", ignore_case=True),
            ),
        )

        assert isinstance(query, LogicOperator)
        assert len(query.operations) == 7

    def test_log_analysis_query(self) -> None:
        p = self.predicate

        query = p.and_(
            p.eq("log_level", "ERROR"),
            p.gte("timestamp", "2024-01-01T00:00:00Z"),
            p.lte("timestamp", "2024-01-07T23:59:59Z"),
            p.not_in("error_code", ["E001", "E002", "E003"]),
            p.or_(
                p.contains("message", "database", ignore_case=True),
                p.contains("message", "timeout", ignore_case=True),
                p.regex("message", r".*connection.*failed.*"),
            ),
        )

        assert isinstance(query, LogicOperator)
        assert len(query.operations) == 5
