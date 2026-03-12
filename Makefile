.PHONY: test lint typecheck coverage ci

test:
	python -m pytest tests/ -q -m "not e2e"

lint:
	ruff check .
	ruff format --check .

typecheck:
	pyright

coverage:
	python -m pytest tests/ -m "not e2e" --cov=generators --cov=bridge --cov-branch --cov-report=term-missing -q

ci: lint typecheck test
