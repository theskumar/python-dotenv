# python-dotenv

[![Build Status][build_status_badge]][build_status_link]
[![PyPI version][pypi_badge]][pypi_link]

python-dotenv reads key-value pairs from a `.env` file and can set them as
environment variables. It helps in the development of applications following the
[12-factor](https://12factor.net/) principles.

> **[Read the full documentation](https://theskumar.github.io/python-dotenv/)**

## Getting Started

```shell
pip install python-dotenv
```

If your application takes its configuration from environment variables, like a
12-factor application, launching it in development is not very practical because
you have to set those environment variables yourself.

To help you with that, you can add python-dotenv to your application to make it
load the configuration from a `.env` file when it is present (e.g. in
development) while remaining configurable via the environment:

```python
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file and sets them in os.environ

# Code of your application, which uses environment variables (e.g. from `os.environ` or
# `os.getenv`) as if they came from the actual environment.
```

By default, `load_dotenv()` will:

- Look for a `.env` file in the same directory as the Python script (or higher up the directory tree).
- Read each key-value pair and add it to `os.environ`.
- **Not override** existing environment variables (`override=False`). Pass `override=True` to override existing variables.

To configure the development environment, add a `.env` in the root directory of
your project:

```
.
├── .env
└── foo.py
```

The syntax of `.env` files supported by python-dotenv is similar to that of
Bash:

```bash
# Development settings
DOMAIN=example.org
ADMIN_EMAIL=admin@${DOMAIN}
ROOT_URL=${DOMAIN}/app
```

If you use variables in values, ensure they are surrounded with `{` and `}`,
like `${DOMAIN}`, as bare variables such as `$DOMAIN` are not expanded.

You will probably want to add `.env` to your `.gitignore`, especially if it
contains secrets like a password.

See the [file format specification](https://theskumar.github.io/python-dotenv/reference/file-format/)
for full details on `.env` syntax, multiline values, escape sequences, and
variable expansion.

## Related Projects

- [environs](https://github.com/sloria/environs)
- [Honcho](https://github.com/nickstenning/honcho)
- [dump-env](https://github.com/sobolevn/dump-env)
- [dynaconf](https://github.com/dynaconf/dynaconf)
- [parse_it](https://github.com/naorlivne/parse_it)
- [django-dotenv](https://github.com/jpadilla/django-dotenv)
- [django-environ](https://github.com/joke2k/django-environ)
- [python-decouple](https://github.com/HBNetwork/python-decouple)
- [django-configuration](https://github.com/jezdez/django-configurations)

## Acknowledgements

This project is currently maintained by [Saurabh Kumar][saurabh-homepage] and
[Bertrand Bonnefoy-Claudet][gh-bbc2] and would not have been possible without
the support of these [awesome people][contributors].

[gh-bbc2]: https://github.com/bbc2
[saurabh-homepage]: https://saurabh-kumar.com
[pypi_link]: https://badge.fury.io/py/python-dotenv
[pypi_badge]: https://badge.fury.io/py/python-dotenv.svg
[python_streams]: https://docs.python.org/3/library/io.html
[contributors]: https://github.com/theskumar/python-dotenv/graphs/contributors
[build_status_link]: https://github.com/theskumar/python-dotenv/actions/workflows/test.yml
[build_status_badge]: https://github.com/theskumar/python-dotenv/actions/workflows/test.yml/badge.svg
