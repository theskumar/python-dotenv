import shlex

from dotenv import dotenv_values
from dotenv import get_cli_string as c
from dotenv.cli import cli as dotenv_cli


def test_to_cli_string():
    assert c() == "dotenv"
    assert c(path="/etc/.env") == "dotenv -f /etc/.env"
    assert c(path="/etc/.env", action="list") == "dotenv -f /etc/.env list"
    assert c(action="list") == "dotenv list"
    assert c(action="get", key="DEBUG") == "dotenv get DEBUG"
    assert c(action="set", key="DEBUG", value="True") == "dotenv set DEBUG True"
    assert (
        c(action="set", key="SECRET", value="=@asdfasf")
        == "dotenv set SECRET =@asdfasf"
    )
    assert c(action="set", key="SECRET", value="a b") == 'dotenv set SECRET "a b"'
    assert (
        c(action="set", key="SECRET", value="a b", quote="always")
        == 'dotenv -q always set SECRET "a b"'
    )


def test_to_cli_string_empty_value(cli, dotenv_path):
    command = c(action="set", key="EMPTY", value="")

    assert command == 'dotenv set EMPTY ""'
    result = cli.invoke(
        dotenv_cli, ["--file", str(dotenv_path), *shlex.split(command)[1:]]
    )

    assert result.exit_code == 0, result.output
    assert dotenv_values(dotenv_path) == {"EMPTY": ""}


def test_to_cli_string_omitted_value():
    assert c(action="set", key="EMPTY", value=None) == "dotenv set EMPTY"
