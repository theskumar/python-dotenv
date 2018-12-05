# -*- coding: utf-8 -*-
import os
from os.path import dirname, join

import pytest
import sh

import dotenv
from dotenv.cli import cli as dotenv_cli
from dotenv.version import __version__

here = dirname(__file__)
dotenv_path = join(here, '.env')


def test_get_key():
    sh.touch(dotenv_path)
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_path, 'HELLO', 'WORLD')
    stored_value = dotenv.get_key(dotenv_path, 'HELLO')
    assert stored_value == 'WORLD'
    sh.rm(dotenv_path)
    assert dotenv.get_key(dotenv_path, 'HELLO') is None
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_path, 'HELLO', 'WORLD')
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


def test_empty_value():
    with open(dotenv_path, "w") as f:
        f.write("TEST=")
    assert dotenv.get_key(dotenv_path, "TEST") == ""
    sh.rm(dotenv_path)


def test_key_value_without_quotes():
    with open(dotenv_path, 'w') as f:
        f.write("TEST = value \n")
    assert dotenv.get_key(dotenv_path, 'TEST') == "value"
    sh.rm(dotenv_path)

    with open(dotenv_path, 'w') as f:
        f.write('TEST = " with spaces " \n')
    assert dotenv.get_key(dotenv_path, 'TEST') == " with spaces "
    sh.rm(dotenv_path)


def test_value_with_quotes():
    with open(dotenv_path, 'w') as f:
        f.write('TEST="two words"\n')
    assert dotenv.get_key(dotenv_path, 'TEST') == 'two words'
    sh.rm(dotenv_path)

    with open(dotenv_path, 'w') as f:
        f.write("TEST='two words'\n")
    assert dotenv.get_key(dotenv_path, 'TEST') == 'two words'
    sh.rm(dotenv_path)


def test_value_with_special_characters():
    with open(dotenv_path, 'w') as f:
        f.write(r'TEST="}=&~{,(\5%{&;"')
    assert dotenv.get_key(dotenv_path, 'TEST') == r'}=&~{,(\5%{&;'
    sh.rm(dotenv_path)

    with open(dotenv_path, 'w') as f:
        f.write(r"TEST='}=&~{,(\5%{&;'")
    assert dotenv.get_key(dotenv_path, 'TEST') == r'}=&~{,(\5%{&;'
    sh.rm(dotenv_path)


def test_value_with_new_lines():
    with open(dotenv_path, 'w') as f:
        f.write('TEST="a\nb"')
    assert dotenv.get_key(dotenv_path, 'TEST') == "a\nb"
    sh.rm(dotenv_path)

    with open(dotenv_path, 'w') as f:
        f.write("TEST='a\nb'")
    assert dotenv.get_key(dotenv_path, 'TEST') == "a\nb"
    sh.rm(dotenv_path)


def test_value_after_comment():
    with open(dotenv_path, "w") as f:
        f.write("# comment\nTEST=a")
    assert dotenv.get_key(dotenv_path, "TEST") == "a"
    sh.rm(dotenv_path)


def test_unset_ok(dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write("a=b\nc=d")

    success, key_to_unset = dotenv.unset_key(dotenv_file, "a")

    assert success is True
    assert key_to_unset == "a"
    with open(dotenv_file, "r") as f:
        assert f.read() == "c=d"
    sh.rm(dotenv_file)


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


def test_console_script(cli):
    TEST_COMBINATIONS = (
        # quote_mode, var_name, var_value, expected_result
        ("always", "HELLO", "WORLD", 'HELLO="WORLD"\n'),
        ("never", "HELLO", "WORLD", 'HELLO=WORLD\n'),
        ("auto", "HELLO", "WORLD", 'HELLO=WORLD\n'),
        ("auto", "HELLO", "HELLO WORLD", 'HELLO="HELLO WORLD"\n'),
    )
    with cli.isolated_filesystem():
        for quote_mode, variable, value, expected_result in TEST_COMBINATIONS:
            sh.touch(dotenv_path)
            sh.dotenv('-f', dotenv_path, '-q', quote_mode, 'set', variable, value)
            output = sh.cat(dotenv_path)
            assert output == expected_result
            sh.rm(dotenv_path)

    # should fail for not existing file
    result = cli.invoke(dotenv.cli.set, ['my_key', 'my_value'])
    assert result.exit_code != 0

    # should fail for not existing file
    result = cli.invoke(dotenv.cli.get, ['my_key'])
    assert result.exit_code != 0

    # should fail for not existing file
    result = cli.invoke(dotenv.cli.list, [])
    assert result.exit_code != 0


def test_default_path(cli):
    with cli.isolated_filesystem():
        sh.touch(dotenv_path)
        sh.cd(here)
        sh.dotenv('set', 'HELLO', 'WORLD')
        output = sh.dotenv('get', 'HELLO')
        assert output == 'HELLO=WORLD\n'
        sh.rm(dotenv_path)


def test_get_key_with_interpolation(cli):
    with cli.isolated_filesystem():
        sh.touch(dotenv_path)
        dotenv.set_key(dotenv_path, 'HELLO', 'WORLD')
        dotenv.set_key(dotenv_path, 'FOO', '${HELLO}')
        dotenv.set_key(dotenv_path, 'BAR', 'CONCATENATED_${HELLO}_POSIX_VAR')

        lines = list(open(dotenv_path, "r").readlines())
        assert lines == [
            'HELLO="WORLD"\n',
            'FOO="${HELLO}"\n',
            'BAR="CONCATENATED_${HELLO}_POSIX_VAR"\n',
        ]

        # test replace from variable in file
        stored_value = dotenv.get_key(dotenv_path, 'FOO')
        assert stored_value == 'WORLD'
        stored_value = dotenv.get_key(dotenv_path, 'BAR')
        assert stored_value == 'CONCATENATED_WORLD_POSIX_VAR'
        # test replace from environ taking precedence over file
        os.environ["HELLO"] = "TAKES_PRECEDENCE"
        stored_value = dotenv.get_key(dotenv_path, 'FOO')
        assert stored_value == "TAKES_PRECEDENCE"
        sh.rm(dotenv_path)


def test_get_key_with_interpolation_of_unset_variable(cli):
    with cli.isolated_filesystem():
        sh.touch(dotenv_path)
        dotenv.set_key(dotenv_path, 'FOO', '${NOT_SET}')
        # test unavailable replacement returns empty string
        stored_value = dotenv.get_key(dotenv_path, 'FOO')
        assert stored_value == ''
        # unless present in environment
        os.environ['NOT_SET'] = 'BAR'
        stored_value = dotenv.get_key(dotenv_path, 'FOO')
        assert stored_value == 'BAR'
        del(os.environ['NOT_SET'])
        sh.rm(dotenv_path)


def test_run(cli):
    with cli.isolated_filesystem():
        sh.touch(dotenv_path)
        sh.cd(here)
        dotenv.set_key(dotenv_path, 'FOO', 'BAR')
        result = sh.dotenv('run', 'printenv', 'FOO').strip()
        assert result == 'BAR'


def test_run_with_other_env(cli):
    DOTENV_FILE = 'dotenv'
    with cli.isolated_filesystem():
        sh.cd(here)
        sh.touch(DOTENV_FILE)
        sh.dotenv('--file', DOTENV_FILE, 'set', 'FOO', 'BAR')
        result = sh.dotenv('--file', DOTENV_FILE, 'run', 'printenv', 'FOO').strip()
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
