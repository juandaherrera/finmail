clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache
	find . -regex ".*/__pycache__" -exec rm -rf {} +
	pre-commit clean || true

install:
	uv sync --all-extras
	uv export -o requirements.txt

start:
	func start

ruff:
	ruff check --fix
	ruff format

test:
	pytest

pre-commit:
	pre-commit run -a --hook-stage manual $(hook)
