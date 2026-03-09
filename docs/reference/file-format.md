---
icon: lucide/file-text
---

# File Format

The format is not formally specified and still improves over time. That being
said, `.env` files should mostly look like Bash files. Reading from FIFOs (named
pipes) on Unix systems is also supported.

## Keys and values

Keys can be unquoted or single-quoted. Values can be unquoted, single-quoted,
or double-quoted. Spaces before and after keys, equal signs, and values are
ignored.

```bash
# Unquoted
USER=foo

# Single-quoted key and value
'USER'='foo'

# Double-quoted value
USER="foo"
```

Lines can start with the `export` directive, which does not affect their
interpretation:

```bash
export USER=foo
```

## Comments

Lines starting with `#` are comments:

```bash
# This is a comment
USER=foo
```

Unquoted values can have inline comments after whitespace:

```bash
USER=foo  # this is a comment
```

Inline comments are not supported in quoted values. The `#` becomes part of
the value:

```bash
USER="foo  # this is NOT a comment"
```

## Escape sequences

**In single-quoted values:** `\\`, `\'`

**In double-quoted values:** `\\`, `\'`, `\"`, `\a`, `\b`, `\f`, `\n`, `\r`, `\t`, `\v`

Unquoted values do not support escape sequences.

## Multiline values

Single- or double-quoted values can span multiple lines. The following are
equivalent:

```bash
FOO="first line
second line"
```

```bash
FOO="first line\nsecond line"
```

Unquoted values cannot span multiple lines.

## Variable without a value

A variable can have no value:

```bash
FOO
```

`dotenv_values` returns `None` for such keys (e.g. `{"FOO": None}`).
`load_dotenv` ignores them.

This is different from `FOO=`, which sets the variable to an empty string.

## Variable expansion

python-dotenv can interpolate variables using POSIX variable expansion.

Variables must use the `${VAR}` syntax with braces:

```bash
DOMAIN=example.org
ADMIN_EMAIL=admin@${DOMAIN}
```

Bare variables like `$DOMAIN` (without braces) are **not** expanded.

Default values are supported with `${VAR:-default}`:

```bash
DATABASE_HOST=${DB_HOST:-localhost}
DATABASE_URL=postgres://${DATABASE_HOST}:5432/mydb
```

If `DB_HOST` is not defined in the `.env` file or the environment, `DATABASE_HOST`
resolves to `localhost`.

### Resolution order

With `load_dotenv(override=True)` or `dotenv_values()`, the value of a variable
is the first of the values defined in the following list:

1. Value of that variable in the `.env` file.
2. Value of that variable in the environment.
3. Default value, if provided.
4. Empty string.

With `load_dotenv(override=False)` (the default), the value of a variable is
the first of the values defined in the following list:

1. Value of that variable in the environment.
2. Value of that variable in the `.env` file.
3. Default value, if provided.
4. Empty string.

!!! note

    `dotenv_values()` does not have an `override` parameter and always resolves
    variables using the `override=True` order above.
