# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import contextlib
import os
import pytest
import tempfile
import warnings
import sh

from dotenv import load_dotenv, find_dotenv, set_key, dotenv_values
from dotenv.main import Binding, parse_stream
from dotenv.compat import StringIO
from IPython.terminal.embed import InteractiveShellEmbed


@contextlib.contextmanager
def restore_os_environ():
    environ = dict(os.environ)

    try:
        yield
    finally:
        os.environ.update(environ)


@pytest.mark.parametrize("test_input,expected", [
    ("", []),
    ("a=b", [Binding(key="a", value="b", original="a=b")]),
    ("'a'=b", [Binding(key="'a'", value="b", original="'a'=b")]),
    ("[=b", [Binding(key="[", value="b", original="[=b")]),
    (" a = b ", [Binding(key="a", value="b", original=" a = b ")]),
    ("export a=b", [Binding(key="a", value="b", original="export a=b")]),
    (" export 'a'=b", [Binding(key="'a'", value="b", original=" export 'a'=b")]),
    (" export 'a'=b", [Binding(key="'a'", value="b", original=" export 'a'=b")]),
    ("# a=b", [Binding(key=None, value=None, original="# a=b")]),
    ('a=b # comment', [Binding(key="a", value="b", original="a=b # comment")]),
    ("a=b space ", [Binding(key="a", value="b space", original="a=b space ")]),
    ("a='b space '", [Binding(key="a", value="b space ", original="a='b space '")]),
    ('a="b space "', [Binding(key="a", value="b space ", original='a="b space "')]),
    ("export export_a=1", [Binding(key="export_a", value="1", original="export export_a=1")]),
    ("export port=8000", [Binding(key="port", value="8000", original="export port=8000")]),
    ('a="b\nc"', [Binding(key="a", value="b\nc", original='a="b\nc"')]),
    ("a='b\nc'", [Binding(key="a", value="b\nc", original="a='b\nc'")]),
    ('a="b\nc"', [Binding(key="a", value="b\nc", original='a="b\nc"')]),
    ('a="b\\nc"', [Binding(key="a", value='b\nc', original='a="b\\nc"')]),
    ('a="b\\"c"', [Binding(key="a", value='b"c', original='a="b\\"c"')]),
    ("a='b\\'c'", [Binding(key="a", value="b'c", original="a='b\\'c'")]),
    ("a=à", [Binding(key="a", value="à", original="a=à")]),
    ('a="à"', [Binding(key="a", value="à", original='a="à"')]),
    ('garbage', [Binding(key=None, value=None, original="garbage")]),
    (
        "a=b\nc=d",
        [
            Binding(key="a", value="b", original="a=b\n"),
            Binding(key="c", value="d", original="c=d"),
        ],
    ),
    (
        "a=b\r\nc=d",
        [
            Binding(key="a", value="b", original="a=b\r\n"),
            Binding(key="c", value="d", original="c=d"),
        ],
    ),
    (
        'a="\nb=c',
        [
            Binding(key="a", value='"', original='a="\n'),
            Binding(key="b", value='c', original="b=c"),
        ]
    ),
    (
        '# comment\na="b\nc"\nd=e\n',
        [
            Binding(key=None, value=None, original="# comment\n"),
            Binding(key="a", value="b\nc", original='a="b\nc"\n'),
            Binding(key="d", value="e", original="d=e\n"),
        ],
    ),
    (
        'garbage[%$#\na=b',
        [
            Binding(key=None, value=None, original="garbage[%$#\n"),
            Binding(key="a", value="b", original='a=b'),
        ],
    ),
])
def test_parse_stream(test_input, expected):
    result = parse_stream(StringIO(test_input))

    assert list(result) == expected


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


def test_dotenv_empty_selfreferential_interpolation():
    stream = StringIO(u'some_path="${some_path}:a/b/c"\n')
    stream.seek(0)
    assert u'some_path' not in os.environ
    parsed_dict = dotenv_values(stream=stream)
    assert {u'some_path': u':a/b/c'} == parsed_dict


def test_dotenv_nonempty_selfreferential_interpolation():
    stream = StringIO(u'some_path="${some_path}:a/b/c"\n')
    stream.seek(0)
    assert u'some_path' not in os.environ
    with restore_os_environ():
        os.environ[u'some_path'] = u'x/y/z'
        parsed_dict = dotenv_values(stream=stream)
    assert {u'some_path': u'x/y/z:a/b/c'} == parsed_dict
