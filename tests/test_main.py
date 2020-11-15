# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os
import sys
import textwrap

import mock
import pytest
import sh

import dotenv
from dotenv.compat import PY2, StringIO


def test_set_key_no_file(tmp_path):
    nx_file = str(tmp_path / "nx")
    logger = logging.getLogger("dotenv.main")

    with mock.patch.object(logger, "warning"):
        result = dotenv.set_key(nx_file, "foo", "bar")

    assert result == (True, "foo", "bar")
    assert os.path.exists(nx_file)


@pytest.mark.parametrize(
    "before,key,value,expected,after",
    [
        ("", "a", "", (True, "a", ""), 'a=""\n'),
        ("", "a", "b", (True, "a", "b"), 'a="b"\n'),
        ("", "a", "'b'", (True, "a", "b"), 'a="b"\n'),
        ("", "a", "\"b\"", (True, "a", "b"), 'a="b"\n'),
        ("", "a", "b'c", (True, "a", "b'c"), 'a="b\'c"\n'),
        ("", "a", "b\"c", (True, "a", "b\"c"), 'a="b\\\"c"\n'),
        ("a=b", "a", "c", (True, "a", "c"), 'a="c"\n'),
        ("a=b\n", "a", "c", (True, "a", "c"), 'a="c"\n'),
        ("a=b\n\n", "a", "c", (True, "a", "c"), 'a="c"\n\n'),
        ("a=b\nc=d", "a", "e", (True, "a", "e"), 'a="e"\nc=d'),
        ("a=b\nc=d\ne=f", "c", "g", (True, "c", "g"), 'a=b\nc="g"\ne=f'),
        ("a=b\n", "c", "d", (True, "c", "d"), 'a=b\nc="d"\n'),
    ],
)
def test_set_key(dotenv_file, before, key, value, expected, after):
    logger = logging.getLogger("dotenv.main")
    with open(dotenv_file, "w") as f:
        f.write(before)

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.set_key(dotenv_file, key, value)

    assert result == expected
    assert open(dotenv_file, "r").read() == after
    mock_warning.assert_not_called()


def test_set_key_permission_error(dotenv_file):
    os.chmod(dotenv_file, 0o000)

    with pytest.raises(Exception):
        dotenv.set_key(dotenv_file, "a", "b")

    os.chmod(dotenv_file, 0o600)
    with open(dotenv_file, "r") as fp:
        assert fp.read() == ""


def test_get_key_no_file(tmp_path):
    nx_file = str(tmp_path / "nx")
    logger = logging.getLogger("dotenv.main")

    with mock.patch.object(logger, "info") as mock_info, \
            mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.get_key(nx_file, "foo")

    assert result is None
    mock_info.assert_has_calls(
        calls=[
            mock.call("Python-dotenv could not find configuration file %s.", nx_file)
        ],
    )
    mock_warning.assert_has_calls(
        calls=[
            mock.call("Key %s not found in %s.", "foo", nx_file)
        ],
    )


def test_get_key_not_found(dotenv_file):
    logger = logging.getLogger("dotenv.main")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.get_key(dotenv_file, "foo")

    assert result is None
    mock_warning.assert_called_once_with("Key %s not found in %s.", "foo", dotenv_file)


def test_get_key_ok(dotenv_file):
    logger = logging.getLogger("dotenv.main")
    with open(dotenv_file, "w") as f:
        f.write("foo=bar")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.get_key(dotenv_file, "foo")

    assert result == "bar"
    mock_warning.assert_not_called()


def test_get_key_none(dotenv_file):
    logger = logging.getLogger("dotenv.main")
    with open(dotenv_file, "w") as f:
        f.write("foo")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.get_key(dotenv_file, "foo")

    assert result is None
    mock_warning.assert_not_called()


def test_unset_with_value(dotenv_file):
    logger = logging.getLogger("dotenv.main")
    with open(dotenv_file, "w") as f:
        f.write("a=b\nc=d")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.unset_key(dotenv_file, "a")

    assert result == (True, "a")
    with open(dotenv_file, "r") as f:
        assert f.read() == "c=d"
    mock_warning.assert_not_called()


def test_unset_no_value(dotenv_file):
    logger = logging.getLogger("dotenv.main")
    with open(dotenv_file, "w") as f:
        f.write("foo")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.unset_key(dotenv_file, "foo")

    assert result == (True, "foo")
    with open(dotenv_file, "r") as f:
        assert f.read() == ""
    mock_warning.assert_not_called()


def test_unset_non_existent_file(tmp_path):
    nx_file = str(tmp_path / "nx")
    logger = logging.getLogger("dotenv.main")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.unset_key(nx_file, "foo")

    assert result == (None, "foo")
    mock_warning.assert_called_once_with(
        "Can't delete from %s - it doesn't exist.",
        nx_file,
    )


def prepare_file_hierarchy(path):
    """
    Create a temporary folder structure like the following:

        test_find_dotenv0/
        └── child1
            ├── child2
            │   └── child3
            │       └── child4
            └── .env

    Then try to automatically `find_dotenv` starting in `child4`
    """

    curr_dir = path
    dirs = []
    for f in ['child1', 'child2', 'child3', 'child4']:
        curr_dir /= f
        dirs.append(curr_dir)
        curr_dir.mkdir()

    return (dirs[0], dirs[-1])


def test_find_dotenv_no_file_raise(tmp_path):
    (root, leaf) = prepare_file_hierarchy(tmp_path)
    os.chdir(str(leaf))

    with pytest.raises(IOError):
        dotenv.find_dotenv(raise_error_if_not_found=True, usecwd=True)


def test_find_dotenv_no_file_no_raise(tmp_path):
    (root, leaf) = prepare_file_hierarchy(tmp_path)
    os.chdir(str(leaf))

    result = dotenv.find_dotenv(usecwd=True)

    assert result == ""


def test_find_dotenv_found(tmp_path):
    (root, leaf) = prepare_file_hierarchy(tmp_path)
    os.chdir(str(leaf))
    dotenv_file = root / ".env"
    dotenv_file.write_bytes(b"TEST=test\n")

    result = dotenv.find_dotenv(usecwd=True)

    assert result == str(dotenv_file)


@mock.patch.dict(os.environ, {}, clear=True)
def test_load_dotenv_existing_file(dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write("a=b")

    result = dotenv.load_dotenv(dotenv_file)

    assert result is True
    assert os.environ == {"a": "b"}


def test_load_dotenv_no_file_verbose():
    logger = logging.getLogger("dotenv.main")

    with mock.patch.object(logger, "info") as mock_info:
        dotenv.load_dotenv('.does_not_exist', verbose=True)

    mock_info.assert_called_once_with("Python-dotenv could not find configuration file %s.", ".does_not_exist")


@mock.patch.dict(os.environ, {"a": "c"}, clear=True)
def test_load_dotenv_existing_variable_no_override(dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write("a=b")

    result = dotenv.load_dotenv(dotenv_file, override=False)

    assert result is True
    assert os.environ == {"a": "c"}


@mock.patch.dict(os.environ, {"a": "c"}, clear=True)
def test_load_dotenv_existing_variable_override(dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write("a=b")

    result = dotenv.load_dotenv(dotenv_file, override=True)

    assert result is True
    assert os.environ == {"a": "b"}


@mock.patch.dict(os.environ, {"a": "c"}, clear=True)
def test_load_dotenv_redefine_var_used_in_file_no_override(dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write('a=b\nd="${a}"')

    result = dotenv.load_dotenv(dotenv_file)

    assert result is True
    assert os.environ == {"a": "c", "d": "c"}


@mock.patch.dict(os.environ, {"a": "c"}, clear=True)
def test_load_dotenv_redefine_var_used_in_file_with_override(dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write('a=b\nd="${a}"')

    result = dotenv.load_dotenv(dotenv_file, override=True)

    assert result is True
    assert os.environ == {"a": "b", "d": "b"}


@mock.patch.dict(os.environ, {}, clear=True)
def test_load_dotenv_utf_8():
    stream = StringIO("a=à")

    result = dotenv.load_dotenv(stream=stream)

    assert result is True
    if PY2:
        assert os.environ == {"a": "à".encode(sys.getfilesystemencoding())}
    else:
        assert os.environ == {"a": "à"}


def test_load_dotenv_in_current_dir(tmp_path):
    dotenv_path = tmp_path / '.env'
    dotenv_path.write_bytes(b'a=b')
    code_path = tmp_path / 'code.py'
    code_path.write_text(textwrap.dedent("""
        import dotenv
        import os

        dotenv.load_dotenv(verbose=True)
        print(os.environ['a'])
    """))
    os.chdir(str(tmp_path))

    result = sh.Command(sys.executable)(code_path)

    assert result == 'b\n'


def test_dotenv_values_file(dotenv_file):
    with open(dotenv_file, "w") as f:
        f.write("a=b")

    result = dotenv.dotenv_values(dotenv_file)

    assert result == {"a": "b"}


@pytest.mark.parametrize(
    "env,string,interpolate,expected",
    [
        # Defined in environment, with and without interpolation
        ({"b": "c"}, "a=$b", False, {"a": "$b"}),
        ({"b": "c"}, "a=$b", True, {"a": "$b"}),
        ({"b": "c"}, "a=${b}", False, {"a": "${b}"}),
        ({"b": "c"}, "a=${b}", True, {"a": "c"}),
        ({"b": "c"}, "a=${b:-d}", False, {"a": "${b:-d}"}),
        ({"b": "c"}, "a=${b:-d}", True, {"a": "c"}),

        # Defined in file
        ({}, "b=c\na=${b}", True, {"a": "c", "b": "c"}),

        # Undefined
        ({}, "a=${b}", True, {"a": ""}),
        ({}, "a=${b:-d}", True, {"a": "d"}),

        # With quotes
        ({"b": "c"}, 'a="${b}"', True, {"a": "c"}),
        ({"b": "c"}, "a='${b}'", True, {"a": "c"}),

        # With surrounding text
        ({"b": "c"}, "a=x${b}y", True, {"a": "xcy"}),

        # Self-referential
        ({"a": "b"}, "a=${a}", True, {"a": "b"}),
        ({}, "a=${a}", True, {"a": ""}),
        ({"a": "b"}, "a=${a:-c}", True, {"a": "b"}),
        ({}, "a=${a:-c}", True, {"a": "c"}),

        # Reused
        ({"b": "c"}, "a=${b}${b}", True, {"a": "cc"}),

        # Re-defined and used in file
        ({"b": "c"}, "b=d\na=${b}", True, {"a": "d", "b": "d"}),
        ({}, "a=b\na=c\nd=${a}", True, {"a": "c", "d": "c"}),
        ({}, "a=b\nc=${a}\nd=e\nc=${d}", True, {"a": "b", "c": "e", "d": "e"}),
    ],
)
def test_dotenv_values_stream(env, string, interpolate, expected):
    with mock.patch.dict(os.environ, env, clear=True):
        stream = StringIO(string)
        stream.seek(0)

        result = dotenv.dotenv_values(stream=stream, interpolate=interpolate)

        assert result == expected
