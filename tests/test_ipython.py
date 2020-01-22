from __future__ import unicode_literals

import os

import mock


@mock.patch.dict(os.environ, {}, clear=True)
def test_ipython_existing_variable_no_override(tmp_path):
    from IPython.terminal.embed import InteractiveShellEmbed

    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text("a=b\n")
    os.chdir(str(tmp_path))
    os.environ["a"] = "c"

    ipshell = InteractiveShellEmbed()
    ipshell.magic("load_ext dotenv")
    ipshell.magic("dotenv")

    assert os.environ == {"a": "c"}


@mock.patch.dict(os.environ, {}, clear=True)
def test_ipython_existing_variable_override(tmp_path):
    from IPython.terminal.embed import InteractiveShellEmbed

    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text("a=b\n")
    os.chdir(str(tmp_path))
    os.environ["a"] = "c"

    ipshell = InteractiveShellEmbed()
    ipshell.magic("load_ext dotenv")
    ipshell.magic("dotenv -o")

    assert os.environ == {"a": "b"}


@mock.patch.dict(os.environ, {}, clear=True)
def test_ipython_new_variable(tmp_path):
    from IPython.terminal.embed import InteractiveShellEmbed

    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text("a=b\n")
    os.chdir(str(tmp_path))

    ipshell = InteractiveShellEmbed()
    ipshell.magic("load_ext dotenv")
    ipshell.magic("dotenv")

    assert os.environ == {"a": "b"}
