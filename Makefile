.PHONY: clean-pyc clean-build test fmt release

part ?= patch

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

# Cut a release: verify, bump version, commit and tag. See RELEASING.md.
# Override the bump size with `make release part=minor` (default: patch).
release:
	@test "$$(git rev-parse --abbrev-ref HEAD)" = "main" || { echo "Release from main only (currently on $$(git rev-parse --abbrev-ref HEAD))"; exit 1; }
	@git diff --quiet && git diff --cached --quiet || { echo "Working tree is dirty; commit the changelog first"; exit 1; }
	uv run ruff check .
	uv run pytest tests/
	uv run bumpversion $(part)
	@echo ""
	@echo "Tagged v$$(uv run python -c 'import dotenv.version as v; print(v.__version__)'). Next:"
	@echo "  git push origin main --follow-tags"
	@echo "  then create the GitHub Release (see RELEASING.md) to publish to PyPI"
