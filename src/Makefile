# usage: make {command}
# example: make lint
int:
	@echo "Lint project"
	poetry run flake8
	poetry run mypy .
	poetry run black --check .
	poetry run isort --check-only .

fix:
	@echo "Fix project"
	poetry run black .
	poetry run isort .

test:
	@echo "Run tests"
	poetry run pytest
