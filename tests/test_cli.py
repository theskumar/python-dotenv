# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import dirname, join

import dotenv

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
        assert output == 'HELLO="WORLD"\n'
        sh.rm(dotenv_path)
