from pathlib import Path

from pytest import Config


def pytest_ignore_collect(collection_path: Path, config: Config):
    skip = False
    try:
        import sqlalchemy  # noqa: F401
    except ImportError:
        skip = True
    return skip
