from charter._backends.pymongo import PymongoBackend


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
