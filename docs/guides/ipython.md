---
icon: lucide/notebook
---

# IPython & Jupyter

python-dotenv provides a `%dotenv` magic command for IPython and Jupyter sessions.

## Loading the extension

```python
%load_ext dotenv
```

## Usage

Load `.env` from the default location (found automatically via `find_dotenv`):

```python
%dotenv
```

Load from a specific path:

```python
%dotenv relative/or/absolute/path/to/.env
```

## Flags

`-o`
: Override existing environment variables.

`-v`
: Verbose output. Prints each variable as it is loaded.

```python
%dotenv -o -v
```
