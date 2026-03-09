---
icon: lucide/square-terminal
---

# CLI Reference

Requires the `cli` extra. See [CLI Guide](../guides/cli.md#installation) for installation.

## Global options

| Option          | Short | Default  | Description                                                                                |
| --------------- | ----- | -------- | ------------------------------------------------------------------------------------------ |
| `--file PATH`   | `-f`  | `.env`   | Location of the `.env` file in the current working directory.                              |
| `--quote MODE`  | `-q`  | `always` | Quote mode for values when writing: `always`, `never`, or `auto`. Does not affect parsing. |
| `--export BOOL` | `-e`  | `false`  | Prepend `export` to entries when writing with `set`.                                       |
| `--version`     |       |          | Show the version and exit.                                                                 |

## Commands

### `dotenv list`

Display all stored key-value pairs. Output is sorted alphabetically by key. Keys with no value (`None`) are excluded.

```shell
dotenv list
dotenv list --format=json
```

| Option     | Values                              | Default  | Description    |
| ---------- | ----------------------------------- | -------- | -------------- |
| `--format` | `simple`, `json`, `shell`, `export` | `simple` | Output format. |

**Formats:**

- `simple`: `KEY=value` (no quotes)
- `json`: JSON object with indentation, sorted by key
- `shell`: Shell-escaped values (uses `shlex.quote`)
- `export`: Prefixed with `export`, shell-escaped values

### `dotenv set`

Store a key-value pair. Creates the file if it doesn't exist.

```shell
dotenv set KEY value
```

Respects the global `--quote` and `--export` options. Does not follow symlinks.

**Exit code 1** on failure.

### `dotenv get`

Retrieve the value for a key.

```shell
dotenv get KEY
```

**Exit code 1** if the key is not found or has no value.

### `dotenv unset`

Remove a key from the `.env` file.

```shell
dotenv unset KEY
```

Respects the global `--quote` option. Does not follow symlinks.

**Exit code 1** on failure.

### `dotenv run`

Run a command with the `.env` file loaded into the environment.

```shell
dotenv run -- python app.py
dotenv run --no-override -- python app.py
```

| Option                         | Default      | Description                                                    |
| ------------------------------ | ------------ | -------------------------------------------------------------- |
| `--override` / `--no-override` | `--override` | Whether `.env` values override existing environment variables. |

The `.env` file must exist. The command fails with an error if it does not.

**Exit code 1** if no command is given.

On Unix, `dotenv run` replaces the current process with `os.execvpe`. On Windows, it spawns a subprocess.

## Exit codes

| Code | Meaning                                                                                                     |
| ---- | ----------------------------------------------------------------------------------------------------------- |
| `0`  | Success.                                                                                                    |
| `1`  | Command-specific error: key not found (`get`), write failure (`set`, `unset`), or no command given (`run`). |
| `2`  | Could not open the `.env` file.                                                                             |
