from pathlib import Path
from typing import Any

import pytest
from pytest import Config

from charter._backends import load_backend


def pytest_configure(config: Config):
    config.addinivalue_line("markers", "sqlalchemy: mark test as sqlalchemy related")


def pytest_ignore_collect(collection_path: Path, config: Config):
    skip = False
    try:
        import sqlalchemy  # noqa: F401
    except ImportError:
        skip = True
    return skip


@pytest.fixture(scope="session")
def backend() -> Any:
    return load_backend("sqlalchemy")
