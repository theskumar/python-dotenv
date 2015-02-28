# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import dirname, join

import sh
import dotenv

here = dirname(__file__)
dotenv_path = join(here, '.env')


def test_read_write():
    sh.touch(dotenv_path)
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_path, 'HELLO', 'WORLD')
    stored_value = dotenv.get_key(dotenv_path, 'HELLO')
    assert stored_value == 'WORLD'
    sh.rm(dotenv_path)


def test_console_script():
    sh.touch(dotenv_path)
    sh.dotenv('-f', dotenv_path, 'set', 'HELLO', 'WORLD')
    output = sh.dotenv('-f', dotenv_path, 'get', 'HELLO', )
    assert output == 'HELLO="WORLD"\n'
    sh.rm(dotenv_path)


def test_default_path():
    sh.touch(dotenv_path)
    sh.cd(here)
    sh.dotenv('set', 'HELLO', 'WORLD')
    output = sh.dotenv('get', 'HELLO')
    assert output == 'HELLO="WORLD"\n'
    sh.rm(dotenv_path)
