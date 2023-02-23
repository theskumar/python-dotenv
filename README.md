# python-dotenv

[![Build Status][build_status_badge]][build_status_link]
[![PyPI version][pypi_badge]][pypi_link]

Python-dotenv reads key-value pairs from a `.env` file and can set them as environment
variables. It helps in the development of applications following the
[12-factor](http://12factor.net/) principles.

- [Getting Started](#getting-started)
- [Other Use Cases](#other-use-cases)
  * [Load configuration without altering the environment](#load-configuration-without-altering-the-environment)
  * [Parse configuration as a stream](#parse-configuration-as-a-stream)
  * [Load .env files in IPython](#load-env-files-in-ipython)
- [Command-line Interface](#command-line-interface)
- [File format](#file-format)
  * [Multiline values](#multiline-values)
  * [Variable expansion](#variable-expansion)
- [Related Projects](#related-projects)
- [Acknowledgements](#acknowledgements)

## Getting Started

```shell
pip install python-dotenv
```

If your application takes its configuration from environment variables, like a 12-factor
application, launching it in development is not very practical because you have to set
those environment variables yourself.

To help you with that, you can add Python-dotenv to your application to make it load the
configuration from a `.env` file when it is present (e.g. in development) while remaining
configurable via the environment:

```python
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# Code of your application, which uses environment variables (e.g. from `os.environ` or
# `os.getenv`) as if they came from the actual environment.
```

By default, `load_dotenv` doesn't override existing environment variables.

To configure the development environment, add a `.env` in the root directory of your
project:

```
.
├── .env
└── foo.py
```

The syntax of `.env` files supported by python-dotenv is similar to that of Bash:

```bash
# Development settings
DOMAIN=example.org
ADMIN_EMAIL=admin@${DOMAIN}
ROOT_URL=${DOMAIN}/app
```

If you use variables in values, ensure they are surrounded with `{` and `}`, like
`${DOMAIN}`, as bare variables such as `$DOMAIN` are not expanded.

You will probably want to add `.env` to your `.gitignore`, especially if it contains
secrets like a password.

See the section "File format" below for more information about what you can write in a
`.env` file.

## Other Use Cases

### Load configuration without altering the environment

The function `dotenv_values` works more or less the same way as `load_dotenv`, except it
doesn't touch the environment, it just returns a `dict` with the values parsed from the
`.env` file.

```python
from dotenv import dotenv_values

config = dotenv_values(".env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}
```

This notably enables advanced configuration management:

```python
import os
from dotenv import dotenv_values

config = {
    **dotenv_values(".env.shared"),  # load shared development variables
    **dotenv_values(".env.secret"),  # load sensitive variables
    **os.environ,  # override loaded values with environment variables
}
```

### Parse configuration as a stream

`load_dotenv` and `dotenv_values` accept [streams][python_streams] via their `stream`
argument.  It is thus possible to load the variables from sources other than the
filesystem (e.g. the network).

```python
from io import StringIO

from dotenv import load_dotenv

config = StringIO("USER=foo\nEMAIL=foo@example.org")
load_dotenv(stream=config)
```

### Load .env files in IPython

You can use dotenv in IPython.  By default, it will use `find_dotenv` to search for a
`.env` file:

```python
%load_ext dotenv
%dotenv
```

You can also specify a path:

```python
%dotenv relative/or/absolute/path/to/.env
```

Optional flags:

- `-o` to override existing variables.
- `-v` for increased verbosity.

## Command-line Interface

A CLI interface `dotenv` is also included, which helps you manipulate the `.env` file
without manually opening it.

```shell
$ pip install "python-dotenv[cli]"
$ dotenv set USER foo
$ dotenv set EMAIL foo@example.org
$ dotenv list
USER=foo
EMAIL=foo@example.org
$ dotenv list --format=json
{
  "USER": "foo",
  "EMAIL": "foo@example.org"
}
$ dotenv run -- python foo.py
```

Run `dotenv --help` for more information about the options and subcommands.

## File format

The format is not formally specified and still improves over time.  That being said,
`.env` files should mostly look like Bash files.

Keys can be unquoted or single-quoted. Values can be unquoted, single- or double-quoted.
Spaces before and after keys, equal signs, and values are ignored. Values can be followed
by a comment.  Lines can start with the `export` directive, which does not affect their
interpretation.

Allowed escape sequences:

- in single-quoted values: `\\`, `\'`
- in double-quoted values: `\\`, `\'`, `\"`, `\a`, `\b`, `\f`, `\n`, `\r`, `\t`, `\v`

### Multiline values

It is possible for single- or double-quoted values to span multiple lines.  The following
examples are equivalent:

```bash
FOO="first line
second line"
```

```bash
FOO="first line\nsecond line"
```

### Variable without a value

A variable can have no value:

```bash
FOO
```

It results in `dotenv_values` associating that variable name with the value `None` (e.g.
`{"FOO": None}`. `load_dotenv`, on the other hand, simply ignores such variables.

This shouldn't be confused with `FOO=`, in which case the variable is associated with the
empty string.

### Variable expansion

Python-dotenv can interpolate variables using POSIX variable expansion.

With `load_dotenv(override=True)` or `dotenv_values()`, the value of a variable is the
first of the values defined in the following list:

- Value of that variable in the `.env` file.
- Value of that variable in the environment.
- Default value, if provided.
- Empty string.

With `load_dotenv(override=False)`, the value of a variable is the first of the values
defined in the following list:

- Value of that variable in the environment.
- Value of that variable in the `.env` file.
- Default value, if provided.
- Empty string.

## Related Projects

-   [Honcho](https://github.com/nickstenning/honcho) - For managing
    Procfile-based applications.
-   [django-dotenv](https://github.com/jpadilla/django-dotenv)
-   [django-environ](https://github.com/joke2k/django-environ)
-   [django-environ-2](https://github.com/sergeyklay/django-environ-2)
-   [django-configuration](https://github.com/jezdez/django-configurations)
-   [dump-env](https://github.com/sobolevn/dump-env)
-   [environs](https://github.com/sloria/environs)
-   [dynaconf](https://github.com/rochacbruno/dynaconf)
-   [parse_it](https://github.com/naorlivne/parse_it)
-   [python-decouple](https://github.com/HBNetwork/python-decouple)

## Acknowledgements

This project is currently maintained by [Saurabh Kumar](https://saurabh-kumar.com) and
[Bertrand Bonnefoy-Claudet](https://github.com/bbc2) and would not have been possible
without the support of these [awesome
people](https://github.com/theskumar/python-dotenv/graphs/contributors).

[build_status_badge]: https://github.com/theskumar/python-dotenv/actions/workflows/test.yml/badge.svg
[build_status_link]: https://github.com/theskumar/python-dotenv/actions/workflows/test.yml
[pypi_badge]: https://badge.fury.io/py/python-dotenv.svg
[pypi_link]: http://badge.fury.io/py/python-dotenv
[python_streams]: https://docs.python.org/3/library/io.html
