
lint:
	@echo "Lint Project"
	@echo "Usage: make lint"
	poetry run flake8
	poetry run mypy .
	poetry run black --check .
	poetry run isort --check-only .

fix:
	@echo "Lint and fix Project"
	@echo "Usage: make fix"
	poetry run black .
	poetry run isort .

test:
	@echo "Run tests for Project"
	@echo "Usage: make test"
	poetry run pytest
