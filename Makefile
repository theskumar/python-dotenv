.PHONY: clean-pyc clean-build test fmt

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -rf .mypy_cache/
	rm -rf .tox/
	rm -rf site/
	rm -fr dist/
	rm -fr src/*.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

sdist: clean
	python -m build -o dist .
	ls -l dist

test:
	uv pip install -e .
	ruff check .
	pytest tests/

fmt:
	ruff format src tests

coverage:
	coverage run --source=dotenv --omit='*tests*' -m py.test tests/ -v --tb=native
	coverage report

coverage-html: coverage
	coverage html
