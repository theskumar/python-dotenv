import os
import sys
from unittest import mock

import pytest

pytest.importorskip("IPython")


@pytest.mark.skipif(
    sys.platform == "win32", reason="This test assumes case-sensitive variable names"
)
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

    assert os.environ == {"a": "c"}


@pytest.mark.skipif(
    sys.platform == "win32", reason="This test assumes case-sensitive variable names"
)
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

    assert os.environ == {"a": "b"}


@pytest.mark.skipif(
    sys.platform == "win32", reason="This test assumes case-sensitive variable names"
)
@mock.patch.dict(os.environ, {}, clear=True)
def test_ipython_new_variable(tmp_path):
    from IPython.terminal.embed import InteractiveShellEmbed

    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text("a=b\n")
    os.chdir(tmp_path)

    ipshell = InteractiveShellEmbed()
    ipshell.run_line_magic("load_ext", "dotenv")
    ipshell.run_line_magic("dotenv", "")

    assert os.environ == {"a": "b"}
