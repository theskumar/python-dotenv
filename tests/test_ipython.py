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


@mock.patch.dict(os.environ, {}, clear=False)
def test_ipython_path_expands_user(tmp_path, monkeypatch):
    from IPython.terminal.embed import InteractiveShellEmbed

    (tmp_path / ".env").write_text("dotenv_ipython_home=b\n")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    ipshell = InteractiveShellEmbed()
    ipshell.run_line_magic("load_ext", "dotenv")
    ipshell.run_line_magic("dotenv", "~/.env")

    assert os.environ["dotenv_ipython_home"] == "b"


@pytest.mark.parametrize("quote", ['"', "'"])
@pytest.mark.parametrize("path_kind", ["relative", "absolute", "home"])
def test_ipython_quoted_path(tmp_path, monkeypatch, quote, path_kind):
    from IPython.core.error import UsageError
    from IPython.terminal.embed import InteractiveShellEmbed

    directory = tmp_path / "my project"
    directory.mkdir()
    dotenv_file = directory / "app.env"
    dotenv_file.write_text("DOTENV_QUOTED_PATH=loaded\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("DOTENV_QUOTED_PATH", "original")
    paths = {
        "relative": "my project/app.env",
        "absolute": str(dotenv_file),
        "home": "~/my project/app.env",
    }

    ipshell = InteractiveShellEmbed()
    ipshell.run_line_magic("load_ext", "dotenv")
    if sys.platform == "win32" and quote == "'":
        # CommandLineToArgvW does not use single quotes to group arguments.
        with pytest.raises(UsageError):
            ipshell.run_line_magic("dotenv", f"-o {quote}{paths[path_kind]}{quote}")
        assert os.environ["DOTENV_QUOTED_PATH"] == "original"
        return
    ipshell.run_line_magic("dotenv", f"-o {quote}{paths[path_kind]}{quote}")

    assert os.environ["DOTENV_QUOTED_PATH"] == "loaded"


@pytest.mark.parametrize(
    "argument,expected",
    [
        (r'"C:\Users\my project\.env"', r"C:\Users\my project\.env"),
        (r"'C:\Users\my project\.env'", r"C:\Users\my project\.env"),
        (r"C:\Users\project\.env", r"C:\Users\project\.env"),
        ('"my project\'s/.env"', "my project's/.env"),
        ("project's/.env", "project's/.env"),
    ],
)
def test_ipython_path_preserves_literal_characters(argument, expected):
    from IPython.core.error import UsageError

    from dotenv.ipython import IPythonDotEnv

    with mock.patch("dotenv.ipython.find_dotenv", return_value=expected) as find:
        with mock.patch("dotenv.ipython.load_dotenv") as load:
            if sys.platform == "win32" and argument.startswith("'"):
                with pytest.raises(UsageError):
                    IPythonDotEnv().dotenv(argument)
                find.assert_not_called()
                load.assert_not_called()
                return
            IPythonDotEnv().dotenv(argument)

    find.assert_called_once_with(expected, True, True)
    load.assert_called_once_with(expected, verbose=False, override=False)


def test_ipython_path_with_literal_outer_apostrophes(tmp_path, monkeypatch):
    from IPython.terminal.embed import InteractiveShellEmbed

    (tmp_path / "'app.env'").write_text("DOTENV_APOSTROPHE_PATH=loaded\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DOTENV_APOSTROPHE_PATH", raising=False)
    ipshell = InteractiveShellEmbed()
    ipshell.run_line_magic("load_ext", "dotenv")
    ipshell.run_line_magic("dotenv", "\"'app.env'\"")

    assert os.environ["DOTENV_APOSTROPHE_PATH"] == "loaded"


@pytest.mark.parametrize(
    "path", ["'app.env'", "my project/app.env", r"C:\Users\app.env"]
)
def test_ipython_windows_parsed_path_is_unchanged(path):
    from dotenv.ipython import IPythonDotEnv

    args = mock.Mock(dotenv_path=path, verbose=False, override=False)
    with mock.patch("dotenv.ipython.sys", platform="win32", create=True):
        with mock.patch("dotenv.ipython.parse_argstring", return_value=args):
            with mock.patch("dotenv.ipython.find_dotenv", return_value=path) as find:
                with mock.patch("dotenv.ipython.load_dotenv") as load:
                    IPythonDotEnv().dotenv("")

    find.assert_called_once_with(path, True, True)
    load.assert_called_once_with(path, verbose=False, override=False)
