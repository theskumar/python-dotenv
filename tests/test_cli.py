import os
import sh
from pathlib import Path
from typing import List, Optional

import pytest

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
def test_list_single_file(cli, dotenv_path, format: Optional[str], content: str, expected: str):
    dotenv_path.write_text(content + '\n')

    args = ['--file', dotenv_path, 'list']
    if format is not None:
        args.extend(['--format', format])

    result = cli.invoke(dotenv_cli, args)

    assert (result.exit_code, result.output) == (0, expected)


@pytest.mark.parametrize(
    "format,contents,expected",
    (
        (None, ["x='1'", "y='2'"], '''x=1\ny=2\n'''),
        (None, ["x='1'", "x='2'"], '''x=2\n'''),
        (None, ["x='1'\ny='2'", "y='20'\nz='30'"], '''x=1\ny=20\nz=30\n'''),
    )
)
def test_list_multi_file(
    cli,
    dotenv_path,
    extra_dotenv_path,
    format: Optional[str],
    contents: List[str],
    expected: str
):
    dotenv_path.write_text(contents[0] + '\n')
    extra_dotenv_path.write_text(contents[1] + '\n')

    args = ['--file', dotenv_path, '--file', extra_dotenv_path, 'list']
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


def test_get_existing_value_single_file(cli, dotenv_path):
    dotenv_path.write_text("a=b")

    result = cli.invoke(dotenv_cli, ['--file', dotenv_path, 'get', 'a'])

    assert (result.exit_code, result.output) == (0, "b\n")


@pytest.mark.parametrize(
    "contents,expected_values",
    (
        (["a=1", "b=2"], {"a": "1", "b": "2"}),
        (["b=2", "a=1"], {"a": "1", "b": "2"}),
        (["a=1", "a=2"], {"a": "2"}),
    )
)
def test_get_existing_value_multi_file(cli, contents, expected_values, dotenv_path, extra_dotenv_path):
    dotenv_path.write_text(contents[0])
    extra_dotenv_path.write_text(contents[1])

    for key, value in expected_values.items():
        result = cli.invoke(dotenv_cli, ['--file', dotenv_path, '--file', extra_dotenv_path, 'get', key])

        assert (result.exit_code, result.output) == (0, f"{value}\n")


def test_get_non_existent_value(cli, dotenv_path):
    result = cli.invoke(dotenv_cli, ['--file', dotenv_path, 'get', 'a'])
    assert (result.exit_code, result.output) == (1, "")


def test_get_non_existent_file(cli):
    result = cli.invoke(dotenv_cli, ['--file', 'nx_file', 'get', 'a'])

    assert result.exit_code == 2
    assert "Error opening env file" in result.output


def test_get_not_a_file(cli):
    result = cli.invoke(dotenv_cli, ['--file', '.', 'get', 'a'])

    assert result.exit_code == 2
    assert "Error opening env file" in result.output


def test_unset_existing_value(cli, dotenv_path):
    dotenv_path.write_text("a=b")

    result = cli.invoke(dotenv_cli, ['--file', dotenv_path, 'unset', 'a'])

    assert (result.exit_code, result.output) == (0, "Successfully removed a\n")
    assert dotenv_path.read_text() == ""


def test_unset_non_existent_value(cli, dotenv_path):
    result = cli.invoke(dotenv_cli, ['--file', dotenv_path, 'unset', 'a'])

    assert (result.exit_code, result.output) == (1, "")
    assert dotenv_path.read_text() == ""


def test_unset_multi_file_not_allowed(cli, dotenv_path, extra_dotenv_path):
    result = cli.invoke(dotenv_cli, ['--file', dotenv_path, '--file', extra_dotenv_path, 'unset', 'a'])
    assert result.exit_code == 1
    assert result.output == f"Unset is not supported for multiple files: ['{dotenv_path}', '{extra_dotenv_path}'].\n"


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
def test_set_quote_options(cli, dotenv_path, quote_mode, variable, value, expected):
    result = cli.invoke(
        dotenv_cli,
        ["--file", dotenv_path, "--export", "false", "--quote", quote_mode, "set", variable, value]
    )

    assert (result.exit_code, result.output) == (0, "{}={}\n".format(variable, value))
    assert dotenv_path.read_text() == expected


@pytest.mark.parametrize(
    "dotenv_path,export_mode,variable,value,expected",
    (
        (Path(".nx_file"), "true", "a", "x", "export a='x'\n"),
        (Path(".nx_file"), "false", "a", "x", "a='x'\n"),
    )
)
def test_set_export(cli, dotenv_path, export_mode, variable, value, expected):
    result = cli.invoke(
        dotenv_cli,
        ["--file", dotenv_path, "--quote", "always", "--export", export_mode, "set", variable, value]
    )

    assert (result.exit_code, result.output) == (0, "{}={}\n".format(variable, value))
    assert dotenv_path.read_text() == expected


def test_set_non_existent_file(cli):
    result = cli.invoke(dotenv.cli.set, ["a", "b"])

    assert (result.exit_code, result.output) == (1, "")


def test_set_no_file(cli):
    result = cli.invoke(dotenv_cli, ["--file", "nx_file", "set"])

    assert result.exit_code == 2
    assert "Missing argument" in result.output


def test_set_multi_file_not_allowed(cli, dotenv_path, extra_dotenv_path):
    result = cli.invoke(dotenv_cli, ['--file', dotenv_path, '--file', extra_dotenv_path, 'set', 'a', 'b'])
    assert result.exit_code == 1
    assert result.output == f"Set is not supported for multiple files: ['{dotenv_path}', '{extra_dotenv_path}'].\n"


def test_get_default_path(tmp_path):
    with sh.pushd(tmp_path):
        (tmp_path / ".env").write_text("a=b")

        result = sh.dotenv("get", "a")

        assert result == "b\n"


def test_run(tmp_path):
    with sh.pushd(tmp_path):
        (tmp_path / ".env").write_text("a=b")

        result = sh.dotenv("run", "printenv", "a")

        assert result == "b\n"


def test_run_with_existing_variable(tmp_path):
    with sh.pushd(tmp_path):
        (tmp_path / ".env").write_text("a=b")
        env = dict(os.environ)
        env.update({"LANG": "en_US.UTF-8", "a": "c"})

        result = sh.dotenv("run", "printenv", "a", _env=env)

        assert result == "b\n"


def test_run_with_existing_variable_not_overridden(tmp_path):
    with sh.pushd(tmp_path):
        (tmp_path / ".env").write_text("a=b")
        env = dict(os.environ)
        env.update({"LANG": "en_US.UTF-8", "a": "c"})

        result = sh.dotenv("run", "--no-override", "printenv", "a", _env=env)

        assert result == "c\n"


def test_run_with_none_value(tmp_path):
    with sh.pushd(tmp_path):
        (tmp_path / ".env").write_text("a=b\nc")

        result = sh.dotenv("run", "printenv", "a")

        assert result == "b\n"


def test_run_with_other_env(dotenv_path):
    dotenv_path.write_text("a=b")

    result = sh.dotenv("--file", dotenv_path, "run", "printenv", "a")

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
