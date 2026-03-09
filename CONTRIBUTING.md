Contributing
============

All the contributions are welcome! Please open [an
issue](https://github.com/theskumar/python-dotenv/issues/new) or send us
a pull request.

Executing the tests:

    $ uv venv
    $ uv pip install -r requirements.txt
    $ uv pip install -e .
    $ uv ruff check .
    $ uv format .
    $ uv run pytest

or with [tox](https://pypi.org/project/tox/) installed:

    $ tox


Use of pre-commit is recommended:

    $ uv run precommit install


Documentation is published with [mkdocs]():

```shell
$ uv pip install -r requirements-docs.txt
$ uv pip install -e .
$ uv run mkdocs serve
```

Open http://127.0.0.1:8000/ to view the documentation locally.
