lint:
	uv run ruff check . --fix
	uv run mypy charter

test:
	uv run pytest

format:
	uv run ruff format .
