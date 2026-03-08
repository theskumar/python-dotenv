---
icon: lucide/rocket
---

# Getting Started

This tutorial walks you through installing python-dotenv and using it to load
environment variables from a `.env` file.

## Installation

=== "`pip`"

    ```shell
    pip install python-dotenv
    ```

=== "`uv`"

    ```shell
    uv add python-dotenv
    ```

## Create a `.env` file

Add a `.env` file to the root of your project:

```
.
├── .env
└── app.py
```

Write your configuration as key-value pairs:

```bash
# .env
DOMAIN=example.org
ADMIN_EMAIL=admin@${DOMAIN}
ROOT_URL=${DOMAIN}/app
```

If you use variables in values, ensure they are surrounded with `{` and `}`,
like `${DOMAIN}`, as bare variables such as `$DOMAIN` are not expanded. See
[Variable expansion](reference/file-format.md#variable-expansion) for the full
syntax.

!!! tip

    Add `.env` to your `.gitignore`, especially if it contains secrets.

## Load the `.env` file

In your Python application:

```python
from dotenv import load_dotenv
import os

load_dotenv()

domain = os.getenv("DOMAIN")
print(domain)  # example.org
```

`load_dotenv()` looks for a `.env` file starting in the same directory as the
calling script, walking up the directory tree until it finds one. Each key-value
pair is added to `os.environ`.

## How it works

By default, `load_dotenv()`:

- Searches for a `.env` file automatically using `find_dotenv()`.
- Reads each key-value pair and adds it to `os.environ`.
- **Does not override** existing environment variables. Pass `override=True` to change this.

```python
# Override existing environment variables
load_dotenv(override=True)
```

## Next steps

- [Configuration Patterns](guides/configuration.md): load config as a dict, layer multiple `.env` files.
- [Command-line Interface](guides/cli.md): manage `.env` files and run commands from the terminal.
- [File Format](reference/file-format.md): full specification of `.env` file syntax.
- [Python API Reference](reference/api.md): all functions and their parameters.
