import os
from unittest import mock

import pytest


pytest.importorskip("IPython")


def as_env(d: dict):
    if os.name == 'nt':
        # Environment variables are always uppercase for Python on Windows
        return {k.upper():v for k,v in d.items()}
    else:
        return d


@mock.patch.dict(os.environ, {}, clear=True)
def test_ipython_existing_variable_no_override(tmp_path):
    from IPython.terminal.embed import InteractiveShellEmbed

    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text("a=b\n")
    os.chdir(tmp_path)
    os.environ["a"] = "c"

    ipshell = InteractiveShellEmbed()
    ipshell.run_line_magic("load_ext", "dotenv")
    ipshell.run_line_magic("dotenv", "")

    assert os.environ == as_env({"a": "c"})


@mock.patch.dict(os.environ, {}, clear=True)
def test_ipython_existing_variable_override(tmp_path):
    from IPython.terminal.embed import InteractiveShellEmbed

    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text("a=b\n")
    os.chdir(tmp_path)
    os.environ["a"] = "c"

    ipshell = InteractiveShellEmbed()
    ipshell.run_line_magic("load_ext", "dotenv")
    ipshell.run_line_magic("dotenv", "-o")

    assert os.environ == as_env({"a": "b"})


@mock.patch.dict(os.environ, {}, clear=True)
def test_ipython_new_variable(tmp_path):
    from IPython.terminal.embed import InteractiveShellEmbed

    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text("a=b\n")
    os.chdir(tmp_path)

    ipshell = InteractiveShellEmbed()
    ipshell.run_line_magic("load_ext", "dotenv")
    ipshell.run_line_magic("dotenv", "")

    assert os.environ == as_env({"a": "b"})
