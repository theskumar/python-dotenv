import os


def as_env(d: dict):
    if os.name == 'nt':
        # Environment variables are always uppercase for Python on Windows
        return {k.upper(): v for k, v in d.items()}
    else:
        return d
