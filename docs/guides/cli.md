---
icon: lucide/square-terminal
---

# Command-line Interface

python-dotenv includes a `dotenv` CLI for managing `.env` files from the
terminal.

## Installation

The CLI requires the `click` package. Install it with the `cli` extra:

=== "`pip`"

    ```shell
    pip install "python-dotenv[cli]"
    ```

=== "`uv`"

    ```shell
    uv add "python-dotenv[cli]"
    ```

Verify the installation by checking the version:

```shell
dotenv --version
```

!!! info

    The CLI can also be invoked as a Python module: `python -m dotenv`

## Set up your .env from the terminal

Use `set`, `get`, and `unset` to manage key-value pairs:

```shell
dotenv set USER foo
dotenv set EMAIL foo@example.org
dotenv get EMAIL
dotenv unset EMAIL
```

See [CLI Reference](../reference/cli.md) for options such as `--quote` and
`--export`.

## Run a command with .env loaded

Load environment variables from `.env` and execute a command:

```shell
dotenv run -- python app.py
```

By default, `.env` values override existing environment variables. Use
`--no-override` to keep existing values. See [CLI
Reference](../reference/cli.md#dotenv-run) for details.

## Export .env for shell use

List values in a format suitable for sourcing in a shell:

```shell
dotenv list --format=export
```

Other formats include `simple`, `json`, and `shell`. See [CLI
Reference](../reference/cli.md#dotenv-list) for all options.

## Use a non-default .env file

Use `-f` to target a specific file (default is `.env` in the current directory):

```shell
dotenv -f .env.production list
dotenv -f .env.production run -- python app.py
```

## Full CLI reference

See [CLI Reference](../reference/cli.md) for all commands, options, and exit
codes.
