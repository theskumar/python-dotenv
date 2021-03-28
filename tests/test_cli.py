# -*- coding: utf-8 -*-
import pytest
import sh

import dotenv
from dotenv.cli import cli as dotenv_cli
from dotenv.version import __version__


def test_list(cli, dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write("a=b")

    result = cli.invoke(dotenv_cli, ['--file', dotenv_file, 'list'])

    assert (result.exit_code, result.output) == (0, result.output)


def test_list_non_existent_file(cli):
    result = cli.invoke(dotenv_cli, ['--file', 'nx_file', 'list'])

    assert result.exit_code == 2, result.output
    assert "does not exist" in result.output


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


def test_get_no_file(cli):
    result = cli.invoke(dotenv_cli, ['--file', 'nx_file', 'get', 'a'])

    assert result.exit_code == 2
    assert "does not exist" in result.output


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
        ("always", "HELLO", "WORLD", 'HELLO="WORLD"\n'),
        ("never", "HELLO", "WORLD", 'HELLO=WORLD\n'),
        ("auto", "HELLO", "WORLD", 'HELLO=WORLD\n'),
        ("auto", "HELLO", "HELLO WORLD", 'HELLO="HELLO WORLD"\n'),
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
        (".nx_file", "true", "HELLO", "WORLD", "export HELLO=\"WORLD\"\n"),
        (".nx_file", "false", "HELLO", "WORLD", "HELLO=\"WORLD\"\n"),
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
    sh.cd(str(tmp_path))
    with open(str(tmp_path / ".env"), "w") as f:
        f.write("a=b")

    result = sh.dotenv("get", "a")

    assert result == "b\n"


def test_run(tmp_path):
    sh.cd(str(tmp_path))
    dotenv_file = str(tmp_path / ".env")
    with open(dotenv_file, "w") as f:
        f.write("a=b")

    result = sh.dotenv("run", "printenv", "a")

    assert result == "b\n"


def test_run_with_existing_variable(tmp_path):
    sh.cd(str(tmp_path))
    dotenv_file = str(tmp_path / ".env")
    with open(dotenv_file, "w") as f:
        f.write("a=b")

    result = sh.dotenv("run", "printenv", "a", _env={"LANG": "en_US.UTF-8", "a": "c"})

    assert result == "b\n"


def test_run_with_existing_variable_not_overridden(tmp_path):
    sh.cd(str(tmp_path))
    dotenv_file = str(tmp_path / ".env")
    with open(dotenv_file, "w") as f:
        f.write("a=b")

    result = sh.dotenv(
        "run",
        "--no-override",
        "printenv",
        "a",
        _env={"LANG": "en_US.UTF-8", "a": "c"},
    )

    assert result == "c\n"


def test_run_with_none_value(tmp_path):
    sh.cd(str(tmp_path))
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
