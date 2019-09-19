# -*- coding: utf-8 -*-
import os

import pytest
import sh

import dotenv
from dotenv.cli import cli as dotenv_cli
from dotenv.version import __version__


def test_get_key(dotenv_file):
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_file, 'HELLO', 'WORLD')
    stored_value = dotenv.get_key(dotenv_file, 'HELLO')
    assert stored_value == 'WORLD'
    sh.rm(dotenv_file)
    assert dotenv.get_key(dotenv_file, 'HELLO') is None
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_file, 'HELLO', 'WORLD')
    assert success is None


def test_set_key(dotenv_file):
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_file, 'HELLO', 'WORLD')
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_file, 'foo', 'bar')
    assert dotenv.get_key(dotenv_file, 'HELLO') == 'WORLD'

    with open(dotenv_file, 'r') as fp:
        assert 'HELLO="WORLD"\nfoo="bar"' == fp.read().strip()

    success, key_to_set, value_to_set = dotenv.set_key(dotenv_file, 'HELLO', 'WORLD 2')
    assert dotenv.get_key(dotenv_file, 'HELLO') == 'WORLD 2'
    assert dotenv.get_key(dotenv_file, 'foo') == 'bar'

    with open(dotenv_file, 'r') as fp:
        assert 'HELLO="WORLD 2"\nfoo="bar"' == fp.read().strip()

    success, key_to_set, value_to_set = dotenv.set_key(dotenv_file, "HELLO", "WORLD\n3")

    with open(dotenv_file, "r") as fp:
        assert 'HELLO="WORLD\n3"\nfoo="bar"' == fp.read().strip()


def test_set_key_permission_error(dotenv_file):
    os.chmod(dotenv_file, 0o000)

    with pytest.raises(Exception):
        dotenv.set_key(dotenv_file, "HELLO", "WORLD")

    os.chmod(dotenv_file, 0o600)
    with open(dotenv_file, "r") as fp:
        assert fp.read() == ""


def test_list(cli, dotenv_file):
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_file, 'HELLO', 'WORLD')
    result = cli.invoke(dotenv_cli, ['--file', dotenv_file, 'list'])
    assert result.exit_code == 0, result.output
    assert result.output == 'HELLO=WORLD\n'


def test_get_cli(cli, dotenv_file):
    cli.invoke(dotenv_cli, ['--file', dotenv_file, 'set', 'HELLO', "WORLD 1"])
    result = cli.invoke(dotenv_cli, ['--file', dotenv_file, 'get', 'HELLO'])
    assert result.exit_code == 0, result.output
    assert result.output == 'HELLO=WORLD 1\n'


def test_list_wo_file(cli):
    result = cli.invoke(dotenv_cli, ['--file', 'doesnotexists', 'list'])
    assert result.exit_code == 2, result.output
    assert 'Invalid value for "-f"' in result.output


def test_empty_value(dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write("TEST=")
    assert dotenv.get_key(dotenv_file, "TEST") == ""


def test_key_value_without_quotes(dotenv_file):
    with open(dotenv_file, 'w') as f:
        f.write("TEST = value \n")
    assert dotenv.get_key(dotenv_file, 'TEST') == "value"


def test_key_value_without_quotes_with_spaces(dotenv_file):
    with open(dotenv_file, 'w') as f:
        f.write('TEST = " with spaces " \n')
    assert dotenv.get_key(dotenv_file, 'TEST') == " with spaces "


def test_value_with_double_quotes(dotenv_file):
    with open(dotenv_file, 'w') as f:
        f.write('TEST="two words"\n')
    assert dotenv.get_key(dotenv_file, 'TEST') == 'two words'


def test_value_with_simple_quotes(dotenv_file):
    with open(dotenv_file, 'w') as f:
        f.write("TEST='two words'\n")
    assert dotenv.get_key(dotenv_file, 'TEST') == 'two words'


def test_value_with_special_characters(dotenv_file):
    with open(dotenv_file, 'w') as f:
        f.write(r'TEST="}=&~{,(\5%{&;"')
    assert dotenv.get_key(dotenv_file, 'TEST') == r'}=&~{,(\5%{&;'


def test_value_with_new_lines(dotenv_file):
    with open(dotenv_file, 'w') as f:
        f.write('TEST="a\nb"')
    assert dotenv.get_key(dotenv_file, 'TEST') == "a\nb"


def test_value_after_comment(dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write("# comment\nTEST=a")
    assert dotenv.get_key(dotenv_file, "TEST") == "a"


def test_unset_ok(dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write("a=b\nc=d")

    success, key_to_unset = dotenv.unset_key(dotenv_file, "a")

    assert success is True
    assert key_to_unset == "a"
    with open(dotenv_file, "r") as f:
        assert f.read() == "c=d"


def test_unset_non_existing_file():
    success, key_to_unset = dotenv.unset_key('/non-existing', 'HELLO')

    assert success is None


def test_unset_cli(cli, dotenv_file):
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_file, 'TESTHELLO', 'WORLD')
    dotenv.get_key(dotenv_file, 'TESTHELLO') == 'WORLD'
    result = cli.invoke(dotenv_cli, ['--file', dotenv_file, 'unset', 'TESTHELLO'])
    assert result.exit_code == 0, result.output
    assert result.output == 'Successfully removed TESTHELLO\n'
    dotenv.get_key(dotenv_file, 'TESTHELLO') is None
    result = cli.invoke(dotenv_cli, ['--file', dotenv_file, 'unset', 'TESTHELLO'])
    assert result.exit_code == 1, result.output


@pytest.mark.parametrize(
    "quote_mode,variable,value,expected",
    (
        ("always", "HELLO", "WORLD", 'HELLO="WORLD"\n'),
        ("never", "HELLO", "WORLD", 'HELLO=WORLD\n'),
        ("auto", "HELLO", "WORLD", 'HELLO=WORLD\n'),
        ("auto", "HELLO", "HELLO WORLD", 'HELLO="HELLO WORLD"\n'),
    )
)
def test_console_script(quote_mode, variable, value, expected, dotenv_file):
    sh.dotenv('-f', dotenv_file, '-q', quote_mode, 'set', variable, value)

    result = sh.cat(dotenv_file)

    assert result == expected


def test_set_non_existing_file(cli):
    result = cli.invoke(dotenv.cli.set, ['my_key', 'my_value'])

    assert result.exit_code != 0


def test_get_non_existing_file(cli):
    result = cli.invoke(dotenv.cli.get, ['my_key'])

    assert result.exit_code != 0


def test_list_non_existing_file(cli):
    result = cli.invoke(dotenv.cli.set, [])

    assert result.exit_code != 0


def test_default_path(tmp_path):
    sh.cd(str(tmp_path))
    sh.touch(tmp_path / '.env')
    sh.dotenv('set', 'HELLO', 'WORLD')

    result = sh.dotenv('get', 'HELLO')

    assert result == 'HELLO=WORLD\n'


def test_get_key_with_interpolation(dotenv_file):
    sh.touch(dotenv_file)
    dotenv.set_key(dotenv_file, 'HELLO', 'WORLD')
    dotenv.set_key(dotenv_file, 'FOO', '${HELLO}')
    dotenv.set_key(dotenv_file, 'BAR', 'CONCATENATED_${HELLO}_POSIX_VAR')

    with open(dotenv_file) as f:
        lines = f.readlines()
    assert lines == [
        'HELLO="WORLD"\n',
        'FOO="${HELLO}"\n',
        'BAR="CONCATENATED_${HELLO}_POSIX_VAR"\n',
    ]

    # test replace from variable in file
    stored_value = dotenv.get_key(dotenv_file, 'FOO')
    assert stored_value == 'WORLD'
    stored_value = dotenv.get_key(dotenv_file, 'BAR')
    assert stored_value == 'CONCATENATED_WORLD_POSIX_VAR'
    # test replace from environ taking precedence over file
    os.environ["HELLO"] = "TAKES_PRECEDENCE"
    stored_value = dotenv.get_key(dotenv_file, 'FOO')
    assert stored_value == "TAKES_PRECEDENCE"


def test_get_key_with_interpolation_of_unset_variable(dotenv_file):
    dotenv.set_key(dotenv_file, 'FOO', '${NOT_SET}')
    # test unavailable replacement returns empty string
    stored_value = dotenv.get_key(dotenv_file, 'FOO')
    assert stored_value == ''
    # unless present in environment
    os.environ['NOT_SET'] = 'BAR'
    stored_value = dotenv.get_key(dotenv_file, 'FOO')
    assert stored_value == 'BAR'
    del(os.environ['NOT_SET'])


def test_run(tmp_path):
    dotenv_file = tmp_path / '.env'
    dotenv_file.touch()
    sh.cd(str(tmp_path))
    dotenv.set_key(str(dotenv_file), 'FOO', 'BAR')
    result = sh.dotenv('run', 'printenv', 'FOO').strip()
    assert result == 'BAR'


def test_run_with_other_env(tmp_path):
    dotenv_name = 'dotenv'
    dotenv_file = tmp_path / dotenv_name
    dotenv_file.touch()
    sh.cd(str(tmp_path))
    sh.dotenv('--file', dotenv_name, 'set', 'FOO', 'BAR')
    result = sh.dotenv('--file', dotenv_name, 'run', 'printenv', 'FOO').strip()
    assert result == 'BAR'


def test_run_without_cmd(cli):
    result = cli.invoke(dotenv_cli, ['run'])
    assert result.exit_code != 0


def test_run_with_invalid_cmd(cli):
    result = cli.invoke(dotenv_cli, ['run', 'i_do_not_exist'])
    assert result.exit_code != 0


def test_run_with_version(cli):
    result = cli.invoke(dotenv_cli, ['--version'])
    print(vars(result))
    assert result.exit_code == 0
    assert result.output.strip().endswith(__version__)
