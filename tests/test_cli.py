import os

import pytest
import sh
from typing import Optional
import dotenv
from dotenv.cli import cli as dotenv_cli
from dotenv.version import __version__


@pytest.mark.parametrize(
    "format,content,expected",
    (
        (None, "x='a b c'", '''x=a b c\n'''),
        ("simple", "x='a b c'", '''x=a b c\n'''),
        ("simple", """x='"a b c"'""", '''x="a b c"\n'''),
        ("simple", '''x="'a b c'"''', '''x='a b c'\n'''),
        ("json", "x='a b c'", '''{\n  "x": "a b c"\n}\n'''),
        ("shell", "x='a b c'", "x='a b c'\n"),
        ("shell", """x='"a b c"'""", '''x='"a b c"'\n'''),
        ("shell", '''x="'a b c'"''', '''x=''"'"'a b c'"'"''\n'''),
        ("shell", "x='a\nb\nc'", "x='a\nb\nc'\n"),
        ("export", "x='a b c'", '''export x='a b c'\n'''),
    )
)
def test_list(cli, dotenv_file, format: Optional[str], content: str, expected: str):
    with open(dotenv_file, "w") as f:
        f.write(content + '\n')

    args = ['--file', dotenv_file, 'list']
    if format is not None:
        args.extend(['--format', format])

    result = cli.invoke(dotenv_cli, args)

    assert (result.exit_code, result.output) == (0, expected)


def test_list_non_existent_file(cli):
    result = cli.invoke(dotenv_cli, ['--file', 'nx_file', 'list'])

    assert result.exit_code == 2, result.output
    assert "Error opening env file" in result.output


def test_list_not_a_file(cli):
    result = cli.invoke(dotenv_cli, ['--file', '.', 'list'])

    assert result.exit_code == 2, result.output
    assert "Error opening env file" in result.output


def test_list_no_file(cli):
    result = cli.invoke(dotenv.cli.list, [])

    assert (result.exit_code, result.output) == (1, "")


def test_get_existing_value(cli, dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write("a=b")

    result = cli.invoke(dotenv_cli, ['--file', dotenv_file, 'get', 'a'])

    assert (result.exit_code, result.output) == (0, "b\n")


def test_get_non_existent_value(cli, dotenv_file):
    result = cli.invoke(dotenv_cli, ['--file', dotenv_file, 'get', 'a'])

    assert (result.exit_code, result.output) == (1, "")


def test_get_non_existent_file(cli):
    result = cli.invoke(dotenv_cli, ['--file', 'nx_file', 'get', 'a'])

    assert result.exit_code == 2
    assert "Error opening env file" in result.output


def test_get_not_a_file(cli):
    result = cli.invoke(dotenv_cli, ['--file', '.', 'get', 'a'])

    assert result.exit_code == 2
    assert "Error opening env file" in result.output


def test_unset_existing_value(cli, dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write("a=b")

    result = cli.invoke(dotenv_cli, ['--file', dotenv_file, 'unset', 'a'])

    assert (result.exit_code, result.output) == (0, "Successfully removed a\n")
    assert open(dotenv_file, "r").read() == ""


def test_unset_non_existent_value(cli, dotenv_file):
    result = cli.invoke(dotenv_cli, ['--file', dotenv_file, 'unset', 'a'])

    assert (result.exit_code, result.output) == (1, "")
    assert open(dotenv_file, "r").read() == ""


@pytest.mark.parametrize(
    "quote_mode,variable,value,expected",
    (
        ("always", "a", "x", "a='x'\n"),
        ("never", "a", "x", 'a=x\n'),
        ("auto", "a", "x", "a=x\n"),
        ("auto", "a", "x y", "a='x y'\n"),
        ("auto", "a", "$", "a='$'\n"),
    )
)
def test_set_quote_options(cli, dotenv_file, quote_mode, variable, value, expected):
    result = cli.invoke(
        dotenv_cli,
        ["--file", dotenv_file, "--export", "false", "--quote", quote_mode, "set", variable, value]
    )

    assert (result.exit_code, result.output) == (0, "{}={}\n".format(variable, value))
    assert open(dotenv_file, "r").read() == expected


@pytest.mark.parametrize(
    "dotenv_file,export_mode,variable,value,expected",
    (
        (".nx_file", "true", "a", "x", "export a='x'\n"),
        (".nx_file", "false", "a", "x", "a='x'\n"),
    )
)
def test_set_export(cli, dotenv_file, export_mode, variable, value, expected):
    result = cli.invoke(
        dotenv_cli,
        ["--file", dotenv_file, "--quote", "always", "--export", export_mode, "set", variable, value]
    )

    assert (result.exit_code, result.output) == (0, "{}={}\n".format(variable, value))
    assert open(dotenv_file, "r").read() == expected


def test_set_non_existent_file(cli):
    result = cli.invoke(dotenv.cli.set, ["a", "b"])

    assert (result.exit_code, result.output) == (1, "")


def test_set_no_file(cli):
    result = cli.invoke(dotenv_cli, ["--file", "nx_file", "set"])

    assert result.exit_code == 2
    assert "Missing argument" in result.output


def test_get_default_path(tmp_path):
    with sh.pushd(str(tmp_path)):
        with open(str(tmp_path / ".env"), "w") as f:
            f.write("a=b")

        result = sh.dotenv("get", "a")

        assert result == "b\n"


def test_run(tmp_path):
    with sh.pushd(str(tmp_path)):
        dotenv_file = str(tmp_path / ".env")
        with open(dotenv_file, "w") as f:
            f.write("a=b")

        result = sh.dotenv("run", "printenv", "a")

        assert result == "b\n"


def test_run_with_existing_variable(tmp_path):
    with sh.pushd(str(tmp_path)):
        dotenv_file = str(tmp_path / ".env")
        with open(dotenv_file, "w") as f:
            f.write("a=b")
        env = dict(os.environ)
        env.update({"LANG": "en_US.UTF-8", "a": "c"})

        result = sh.dotenv("run", "printenv", "a", _env=env)

        assert result == "b\n"


def test_run_with_existing_variable_not_overridden(tmp_path):
    with sh.pushd(str(tmp_path)):
        dotenv_file = str(tmp_path / ".env")
        with open(dotenv_file, "w") as f:
            f.write("a=b")
        env = dict(os.environ)
        env.update({"LANG": "en_US.UTF-8", "a": "c"})

        result = sh.dotenv("run", "--no-override", "printenv", "a", _env=env)

        assert result == "c\n"


def test_run_with_none_value(tmp_path):
    with sh.pushd(str(tmp_path)):
        dotenv_file = str(tmp_path / ".env")
        with open(dotenv_file, "w") as f:
            f.write("a=b\nc")

        result = sh.dotenv("run", "printenv", "a")

        assert result == "b\n"


def test_run_with_other_env(dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write("a=b")

    result = sh.dotenv("--file", dotenv_file, "run", "printenv", "a")

    assert result == "b\n"


def test_run_without_cmd(cli):
    result = cli.invoke(dotenv_cli, ['run'])

    assert result.exit_code == 2
    assert "Invalid value for '-f'" in result.output


def test_run_with_invalid_cmd(cli):
    result = cli.invoke(dotenv_cli, ['run', 'i_do_not_exist'])

    assert result.exit_code == 2
    assert "Invalid value for '-f'" in result.output


def test_run_with_version(cli):
    result = cli.invoke(dotenv_cli, ['--version'])

    assert result.exit_code == 0
    assert result.output.strip().endswith(__version__)
