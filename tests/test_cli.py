# -*- coding: utf-8 -*-
from os import environ
from os.path import dirname, join

import dotenv
from dotenv.cli import cli as dotenv_cli

import sh

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
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_path, 'HELLO', 'WORLD')
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_path, 'foo', 'bar')
    dotenv.get_key(dotenv_path, 'HELLO') == 'WORLD'

    success, key_to_set, value_to_set = dotenv.set_key(dotenv_path, 'HELLO', 'WORLD 2')
    dotenv.get_key(dotenv_path, 'HELLO') == 'WORLD 2'
    dotenv.get_key(dotenv_path, 'foo') == 'bar'


def test_list(cli, dotenv_file):
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_file, 'HELLO', 'WORLD')
    result = cli.invoke(dotenv_cli, ['--file', dotenv_file, 'list'])
    assert result.exit_code == 0, result.output
    assert result.output == 'HELLO=WORLD\n'


def test_list_wo_file(cli):
    result = cli.invoke(dotenv_cli, ['--file', 'doesnotexists', 'list'])
    assert result.exit_code == 2, result.output
    assert 'Invalid value for "-f"' in result.output


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


def test_unset():
    sh.touch(dotenv_path)
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_path, 'HELLO', 'WORLD')
    stored_value = dotenv.get_key(dotenv_path, 'HELLO')
    assert stored_value == 'WORLD'
    success, key_to_unset = dotenv.unset_key(dotenv_path, 'HELLO')
    assert dotenv.get_key(dotenv_path, 'HELLO') is None
    sh.rm(dotenv_path)
    success, key_to_unset = dotenv.unset_key(dotenv_path, 'HELLO')
    assert success is None


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
        environ["HELLO"] = "TAKES_PRECEDENCE"
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
        environ['NOT_SET'] = 'BAR'
        stored_value = dotenv.get_key(dotenv_path, 'FOO')
        assert stored_value == 'BAR'
        del(environ['NOT_SET'])
        sh.rm(dotenv_path)
