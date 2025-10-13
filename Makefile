.PHONY: clean-pyc clean-build test

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr src/*.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

release: sdist
	twine check dist/*
	twine upload dist/*

release-test: sdist
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

sdist: clean
	python -m build -d dist .
	ls -l dist

test:
	uv pip install -e .
	ruff check .
	pytest tests/

coverage:
	coverage run --source=dotenv --omit='*tests*' -m py.test tests/ -v --tb=native
	coverage report

coverage-html: coverage
	coverage html
