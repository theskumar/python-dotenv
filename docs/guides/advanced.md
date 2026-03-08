---
icon: lucide/atom
---

# Advanced Usage

## Parse configuration from a stream

`load_dotenv` and `dotenv_values` accept text streams via the `stream` argument,
allowing you to load variables from sources other than the filesystem:

```python
from io import StringIO
from dotenv import load_dotenv

config = StringIO("USER=foo\nEMAIL=foo@example.org")
load_dotenv(stream=config)
```

This works with any text stream - `StringIO`, file objects, or responses from
network calls.

## Read from FIFOs (named pipes)

On Unix systems, python-dotenv can read `.env` from a FIFO (named pipe). This is
useful when the `.env` content is generated dynamically:

```shell
mkfifo .env
echo "SECRET=dynamic_value" > .env &
python app.py
```

`find_dotenv()` matches FIFOs in addition to regular files.

## File encoding

All functions that read or write `.env` files accept an `encoding` parameter
(defaults to `utf-8`):

```python
from dotenv import load_dotenv, dotenv_values

load_dotenv(".env", encoding="latin-1")

config = dotenv_values(".env", encoding="latin-1")
```

## Disable `load_dotenv`

Set the `PYTHON_DOTENV_DISABLED` environment variable to disable `load_dotenv()`
from loading `.env` files or streams. Accepted truthy values: `1`, `true`, `t`,
`yes`, `y` (case-insensitive).

```shell
PYTHON_DOTENV_DISABLED=1 python app.py
```

This is useful when you can't modify third-party package calls to `load_dotenv`,
or in production environments where `.env` files should be ignored.

## Controlling file discovery with `find_dotenv`

`find_dotenv()` walks up the directory tree from the calling script's location
until it finds a `.env` file:

```python
from dotenv import find_dotenv

path = find_dotenv()  # returns absolute path or ""
```

Use `usecwd=True` to search from the current working directory instead of the
calling script's directory:

```python
path = find_dotenv(usecwd=True)
```

Search for a file with a different name:

```python
path = find_dotenv(".env.production")
```

Raise an error if the file is not found:

```python
path = find_dotenv(raise_error_if_not_found=True)  # raises IOError
```

In REPL, IPython, frozen, and debugger environments, `find_dotenv` automatically
uses the current working directory.

## Symlink handling

`set_key` and `unset_key` do **not** follow symlinks by default. If your `.env`
is a symlink and you want writes to target the symlink destination, pass
`follow_symlinks=True`:

```python
from dotenv import set_key

set_key(".env", "KEY", "value", follow_symlinks=True)
```

!!! warning

    This behavior changed in v1.2.2. Previously, symlinks were followed in some situations. See the [changelog](../changelog/#122-2026-03-01) for details.

## Debugging with verbose mode

Pass `verbose=True` to log warnings when files are missing or keys are not found:

```python
from dotenv import load_dotenv, get_key

load_dotenv(verbose=True)  # warns if .env is missing
get_key(".env", "MISSING_KEY")  # warns if key not found
```

Messages are emitted via Python's `logging` module under the `dotenv.main`
logger. To see them, configure logging:

```python
import logging

logging.basicConfig()
```
