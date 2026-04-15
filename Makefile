.PHONY: install run test lint clean

install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

run:
	python -m src.main

run-now:
	RUN_ON_STARTUP=true python -m src.main

test:
	pytest

lint:
	ruff check src tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete
