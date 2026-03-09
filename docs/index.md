# python-dotenv

[![Build Status][build_status_badge]][build_status_link]
[![PyPI version][pypi_badge]][pypi_link]

python-dotenv reads key-value pairs from a `.env` file and sets them as
environment variables. It helps in the development of applications following the
[12-factor](https://12factor.net/) principles.

=== "`pip`"

    ```shell
    pip install python-dotenv
    ```

=== "`uv`"

    ```shell
    uv add python-dotenv
    ```

```python
from dotenv import load_dotenv

load_dotenv()  # takes variables from .env and adds them to os.environ
```

## Documentation

<div class="grid cards" markdown>

- [**Getting Started**](getting-started.md) →

  Install python-dotenv and load your first `.env` file.

- [**How-to Guides**](guides/index.md) →

  Recipes for configuration patterns, the CLI, IPython, and advanced usage.

- [**Reference**](reference/index.md) →

  Complete Python API, CLI reference, and `.env` file format specification.

- [**Changelog**](changelog.md) →

  Release history and upgrade notes.

</div>

[pypi_link]: https://badge.fury.io/py/python-dotenv
[pypi_badge]: https://badge.fury.io/py/python-dotenv.svg
[build_status_link]: https://github.com/theskumar/python-dotenv/actions/workflows/test.yml
[build_status_badge]: https://github.com/theskumar/python-dotenv/actions/workflows/test.yml/badge.svg
