from pathlib import Path

from pytest import Config


def pytest_ignore_collect(collection_path: Path, config: Config) -> bool:
    skip = False
    try:
        import pymongo  # noqa: F401
    except ImportError:
        skip = True
    return skip
