# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import pytest
import tempfile
import warnings
import sh

from dotenv import load_dotenv, find_dotenv, set_key, dotenv_values
from dotenv.main import parse_line
from dotenv.compat import StringIO
from IPython.terminal.embed import InteractiveShellEmbed


@pytest.mark.parametrize("test_input,expected", [
    ("a=b", ("a", "b")),
    (" a = b ", ("a", "b")),
    ("export a=b", ("a", "b")),
    (" export 'a'=b", ("'a'", "b")),
    (" export 'a'=b", ("'a'", "b")),
    ("# a=b", (None, None)),
    ("# a=b", (None, None)),
    ("a=b space ", ('a', 'b space')),
    ("a='b space '", ('a', 'b space ')),
    ('a="b space "', ('a', 'b space ')),
])
def test_parse_line(test_input, expected):
    assert parse_line(test_input) == expected


def test_warns_if_file_does_not_exist():
    with warnings.catch_warnings(record=True) as w:
        load_dotenv('.does_not_exist', verbose=True)

        assert len(w) == 1
        assert w[0].category is UserWarning
        assert str(w[0].message) == "File doesn't exist .does_not_exist"


def test_find_dotenv():
    """
    Create a temporary folder structure like the following:

        tmpXiWxa5/
        └── child1
            ├── child2
            │   └── child3
            │       └── child4
            └── .env

    Then try to automatically `find_dotenv` starting in `child4`
    """
    tmpdir = os.path.realpath(tempfile.mkdtemp())

    curr_dir = tmpdir
    dirs = []
    for f in ['child1', 'child2', 'child3', 'child4']:
        curr_dir = os.path.join(curr_dir, f)
        dirs.append(curr_dir)
        os.mkdir(curr_dir)

    child1, child4 = dirs[0], dirs[-1]

    # change the working directory for testing
    os.chdir(child4)

    # try without a .env file and force error
    with pytest.raises(IOError):
        find_dotenv(raise_error_if_not_found=True, usecwd=True)

    # try without a .env file and fail silently
    assert find_dotenv(usecwd=True) == ''

    # now place a .env file a few levels up and make sure it's found
    filename = os.path.join(child1, '.env')
    with open(filename, 'w') as f:
        f.write("TEST=test\n")
    assert find_dotenv(usecwd=True) == filename


def test_load_dotenv(cli):
    dotenv_path = '.test_load_dotenv'
    with cli.isolated_filesystem():
        sh.touch(dotenv_path)
        set_key(dotenv_path, 'DOTENV', 'WORKS')
        assert 'DOTENV' not in os.environ
        success = load_dotenv(dotenv_path)
        assert success
        assert 'DOTENV' in os.environ
        assert os.environ['DOTENV'] == 'WORKS'
        sh.rm(dotenv_path)


def test_load_dotenv_override(cli):
    dotenv_path = '.test_load_dotenv_override'
    key_name = "DOTENV_OVER"

    with cli.isolated_filesystem():
        sh.touch(dotenv_path)
        os.environ[key_name] = "OVERRIDE"
        set_key(dotenv_path, key_name, 'WORKS')
        success = load_dotenv(dotenv_path, override=True)
        assert success
        assert key_name in os.environ
        assert os.environ[key_name] == 'WORKS'
        sh.rm(dotenv_path)


def test_load_dotenv_in_current_dir():
    # make sure were are here!
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    dotenv_path = '.env'
    with open(dotenv_path, 'w') as f:
        f.write("TOTO=bla\n")
    assert 'TOTO' not in os.environ
    success = load_dotenv(verbose=True)
    assert success
    assert os.environ['TOTO'] == 'bla'
    sh.rm(dotenv_path)


def test_ipython():
    tmpdir = os.path.realpath(tempfile.mkdtemp())
    os.chdir(tmpdir)
    filename = os.path.join(tmpdir, '.env')
    with open(filename, 'w') as f:
        f.write("MYNEWVALUE=q1w2e3\n")
    ipshell = InteractiveShellEmbed()
    ipshell.magic("load_ext dotenv")
    ipshell.magic("dotenv")
    assert os.environ["MYNEWVALUE"] == 'q1w2e3'


def test_ipython_override():
    tmpdir = os.path.realpath(tempfile.mkdtemp())
    os.chdir(tmpdir)
    filename = os.path.join(tmpdir, '.env')
    os.environ["MYNEWVALUE"] = "OVERRIDE"
    with open(filename, 'w') as f:
        f.write("MYNEWVALUE=q1w2e3\n")
    ipshell = InteractiveShellEmbed()
    ipshell.magic("load_ext dotenv")
    ipshell.magic("dotenv -o")
    assert os.environ["MYNEWVALUE"] == 'q1w2e3'


def test_dotenv_values_stream():
    stream = StringIO(u'hello="it works!😃"\nDOTENV=${hello}\n')
    stream.seek(0)
    parsed_dict = dotenv_values(stream=stream)
    assert 'DOTENV' in parsed_dict
    assert parsed_dict['DOTENV'] == u'it works!😃'


def test_dotenv_values_export():
    stream = StringIO('export foo=bar\n')
    stream.seek(0)
    load_dotenv(stream=stream)
    assert 'foo' in os.environ
    assert os.environ['foo'] == 'bar'
