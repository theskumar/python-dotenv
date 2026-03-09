---
icon: lucide/bolt
---

# Configuration Patterns

## Load configuration without altering the environment

`dotenv_values` parses a `.env` file and returns a `dict` without modifying
`os.environ`:

```python
from dotenv import dotenv_values

config = dotenv_values(".env")
# config = {"USER": "foo", "EMAIL": "foo@example.org"}
```

This is useful when you need the values but don't want to pollute the global
environment, for example in tests or when passing config explicitly to your
application.

## Per-environment files

Use separate `.env` files for each environment. Load a base file first, then
apply environment-specific overrides:

```python
import os
from dotenv import load_dotenv

load_dotenv(".env")  # shared defaults

env = os.getenv("APP_ENV", "development")
load_dotenv(f".env.{env}", override=True)  # environment-specific overrides
```

`load_dotenv` silently does nothing if the file doesn't exist, so this is safe
to use even when only some override files are present.

A typical file layout:

```
.env                  # shared defaults (committed)
.env.development      # local dev overrides (gitignored)
.env.test             # test overrides (committed or gitignored)
.env.production       # production overrides (gitignored, or use real env vars)
```

The same pattern works with `dotenv_values`:

```python
import os
from dotenv import dotenv_values

env = os.getenv("APP_ENV", "development")
config = {
    **dotenv_values(".env"),            # shared defaults
    **dotenv_values(f".env.{env}"),     # environment overrides
    **os.environ,                       # real environment wins last
}
```

## Layer multiple `.env` files

Combine multiple `.env` files with environment variables for layered
configuration:

```python
import os
from dotenv import dotenv_values

config = {
    **dotenv_values(".env.shared"),  # shared development variables
    **dotenv_values(".env.secret"),  # sensitive variables
    **os.environ,                    # override with real environment
}
```

Later sources override earlier ones, so environment variables take highest
priority.

## Get, set, and unset individual keys

Read a single value from a `.env` file:

```python
from dotenv import get_key

value = get_key(".env", "EMAIL")
```

Write a key-value pair (creates the file if it doesn't exist):

```python
from dotenv import set_key

set_key(".env", "EMAIL", "foo@example.org")
```

Remove a key:

```python
from dotenv import unset_key

unset_key(".env", "EMAIL")
```

## Override behavior

By default, `load_dotenv` does **not** override existing environment variables:

```python
from dotenv import load_dotenv

load_dotenv()                # existing env wins
load_dotenv(override=True)   # .env wins
```

`dotenv_values` always resolves as if `override=True`.

See [Resolution order](../reference/file-format.md#resolution-order) for the
full precedence rules.

## Disable variable interpolation

By default, `${VAR}` references in values are resolved. To treat values as
literal strings, disable interpolation:

```python
from dotenv import load_dotenv, dotenv_values

load_dotenv(interpolate=False)

# or
config = dotenv_values(".env", interpolate=False)
```

This is useful when values contain `$` characters that should not be expanded,
such as passwords.

## Type casting

python-dotenv returns all values as strings. Cast them in your application code:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Integer
db_port = int(os.getenv("DB_PORT", "5432"))

# Boolean - careful, bool("false") is True
debug = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")

# Comma-separated list
allowed_hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
```

For projects with many typed settings, consider
[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
or [python-decouple](https://github.com/HBNetwork/python-decouple), which handle
type casting and validation declaratively.

## Use a `.env.example` template

Commit a `.env.example` file with all required keys but no secret values. This
documents the expected configuration and helps with team onboarding:

```bash
# .env.example - copy to .env and fill in values
SECRET_KEY=change-me
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Optional (defaults shown)
DEBUG=false
LOG_LEVEL=INFO
```

New developers can then run:

```shell
cp .env.example .env
```

Add `.env` to `.gitignore` but keep `.env.example` committed:

```gitignore
.env
.env.production
.env.*.local
!.env.example
```
