.PHONY: clean-pyc clean-build test

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

sdist: clean
	python setup.py sdist
	ls -l dist

test:
	pip install -e .
	flake8 .
	py.test tests/

coverage:
	coverage run --source=dotenv --omit='*tests*' -m py.test tests/ -v --tb=native
	coverage report

coverage-html: coverage
	coverage html
