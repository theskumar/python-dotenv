import shlex
from pathlib import Path

import pytest

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


@pytest.mark.parametrize(
    "directory",
    ["app", "my app", "app's"],
)
@pytest.mark.parametrize("path_type", [str, Path])
def test_to_cli_string_path(cli, tmp_path, directory, path_type):
    project = tmp_path / directory
    project.mkdir()
    path = project / ".env"
    path.write_text("DEBUG=True\n")

    command = c(path=path_type(path), action="get", key="DEBUG")
    result = cli.invoke(dotenv_cli, shlex.split(command)[1:])

    assert (result.exit_code, result.output) == (0, "True\n")
