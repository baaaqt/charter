# from unittest.mock import patch

# import pytest

# from charter._backends import load_backend
# from charter._exc import BackendNotAvailableError


# def test_backend_not_available_error():
#     with patch.dict("sys.modules", {"sqlalchemy": None}):
#         with pytest.raises(BackendNotAvailableError):
#             load_backend("sqlalchemy")
