import io
import logging
import os
import stat
import subprocess
import sys
import textwrap
from unittest import mock

import pytest

import dotenv


def test_set_key_no_file(tmp_path):
    nx_path = tmp_path / "nx"
    logger = logging.getLogger("dotenv.main")

    with mock.patch.object(logger, "warning"):
        result = dotenv.set_key(nx_path, "foo", "bar")

    assert result == (True, "foo", "bar")
    assert nx_path.exists()


@pytest.mark.parametrize(
    "before,key,value,expected,after",
    [
        ("", "a", "", (True, "a", ""), "a=''\n"),
        ("", "a", "b", (True, "a", "b"), "a='b'\n"),
        ("", "a", "'b'", (True, "a", "'b'"), "a='\\'b\\''\n"),
        ("", "a", '"b"', (True, "a", '"b"'), "a='\"b\"'\n"),
        ("", "a", "b'c", (True, "a", "b'c"), "a='b\\'c'\n"),
        ("", "a", 'b"c', (True, "a", 'b"c'), "a='b\"c'\n"),
        ("a=b", "a", "c", (True, "a", "c"), "a='c'\n"),
        ("a=b\n", "a", "c", (True, "a", "c"), "a='c'\n"),
        ("a=b\n\n", "a", "c", (True, "a", "c"), "a='c'\n\n"),
        ("a=b\nc=d", "a", "e", (True, "a", "e"), "a='e'\nc=d"),
        ("a=b\nc=d\ne=f", "c", "g", (True, "c", "g"), "a=b\nc='g'\ne=f"),
        ("a=b\n", "c", "d", (True, "c", "d"), "a=b\nc='d'\n"),
        ("a=b", "c", "d", (True, "c", "d"), "a=b\nc='d'\n"),
    ],
)
def test_set_key(dotenv_path, before, key, value, expected, after):
    logger = logging.getLogger("dotenv.main")
    dotenv_path.write_text(before)

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.set_key(dotenv_path, key, value)

    assert result == expected
    assert dotenv_path.read_text() == after
    mock_warning.assert_not_called()


def test_set_key_encoding(dotenv_path):
    encoding = "latin-1"

    result = dotenv.set_key(dotenv_path, "a", "é", encoding=encoding)

    assert result == (True, "a", "é")
    assert dotenv_path.read_text(encoding=encoding) == "a='é'\n"


@pytest.mark.skipif(
    sys.platform == "win32", reason="file mode bits behave differently on Windows"
)
def test_set_key_preserves_file_mode(dotenv_path):
    dotenv_path.write_text("a=x\n")
    dotenv_path.chmod(0o640)
    mode_before = stat.S_IMODE(dotenv_path.stat().st_mode)

    dotenv.set_key(dotenv_path, "a", "y")

    mode_after = stat.S_IMODE(dotenv_path.stat().st_mode)
    assert mode_before == mode_after


def test_rewrite_closes_file_handle_on_lstat_failure(tmp_path):
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("a=x\n")
    real_open = open
    opened_handles = []

    def tracking_open(*args, **kwargs):
        handle = real_open(*args, **kwargs)
        opened_handles.append(handle)
        return handle

    with mock.patch("dotenv.main.os.lstat", side_effect=FileNotFoundError):
        with mock.patch("dotenv.main.open", side_effect=tracking_open):
            dotenv.set_key(dotenv_path, "a", "x")

    assert opened_handles, "expected at least one file to be opened"
    assert all(handle.closed for handle in opened_handles)


@pytest.mark.skipif(
    sys.platform == "win32", reason="symlinks require elevated privileges on Windows"
)
def test_set_key_symlink_to_existing_file(tmp_path):
    target = tmp_path / "target.env"
    target.write_text("a=x\n")
    symlink = tmp_path / ".env"
    symlink.symlink_to(target)

    dotenv.set_key(symlink, "a", "y")

    assert target.read_text() == "a=x\n"
    assert not symlink.is_symlink()
    assert "a='y'" in symlink.read_text()
    assert stat.S_IMODE(symlink.stat().st_mode) == 0o600


@pytest.mark.skipif(
    sys.platform == "win32", reason="symlinks require elevated privileges on Windows"
)
def test_set_key_symlink_to_missing_file(tmp_path):
    target = tmp_path / "nx"
    symlink = tmp_path / ".env"
    symlink.symlink_to(target)

    dotenv.set_key(symlink, "a", "x")

    assert not target.exists()
    assert not symlink.is_symlink()
    assert symlink.read_text() == "a='x'\n"


@pytest.mark.skipif(
    sys.platform == "win32", reason="symlinks require elevated privileges on Windows"
)
def test_set_key_follow_symlinks(tmp_path):
    target = tmp_path / "target.env"
    target.write_text("a=x\n")
    symlink = tmp_path / ".env"
    symlink.symlink_to(target)

    dotenv.set_key(symlink, "a", "y", follow_symlinks=True)

    assert target.read_text() == "a='y'\n"
    assert symlink.is_symlink()


@pytest.mark.skipif(
    sys.platform != "win32" and os.geteuid() == 0,
    reason="Root user can access files even with 000 permissions.",
)
def test_set_key_permission_error(dotenv_path):
    if sys.platform == "win32":
        # On Windows, make file read-only
        dotenv_path.chmod(stat.S_IREAD)
    else:
        # On Unix, remove all permissions
        dotenv_path.chmod(0o000)

    with pytest.raises(PermissionError):
        dotenv.set_key(dotenv_path, "a", "b")

    # Restore permissions
    if sys.platform == "win32":
        dotenv_path.chmod(stat.S_IWRITE | stat.S_IREAD)
    else:
        dotenv_path.chmod(0o600)
    assert dotenv_path.read_text() == ""


def test_get_key_no_file(tmp_path):
    nx_path = tmp_path / "nx"
    logger = logging.getLogger("dotenv.main")

    with (
        mock.patch.object(logger, "info") as mock_info,
        mock.patch.object(logger, "warning") as mock_warning,
    ):
        result = dotenv.get_key(nx_path, "foo")

    assert result is None
    mock_info.assert_has_calls(
        calls=[
            mock.call("python-dotenv could not find configuration file %s.", nx_path)
        ],
    )
    mock_warning.assert_has_calls(
        calls=[mock.call("Key %s not found in %s.", "foo", nx_path)],
    )


def test_get_key_not_found(dotenv_path):
    logger = logging.getLogger("dotenv.main")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.get_key(dotenv_path, "foo")

    assert result is None
    mock_warning.assert_called_once_with("Key %s not found in %s.", "foo", dotenv_path)


def test_get_key_ok(dotenv_path):
    logger = logging.getLogger("dotenv.main")
    dotenv_path.write_text("foo=bar")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.get_key(dotenv_path, "foo")

    assert result == "bar"
    mock_warning.assert_not_called()


def test_get_key_encoding(dotenv_path):
    encoding = "latin-1"
    dotenv_path.write_text("é=è", encoding=encoding)

    result = dotenv.get_key(dotenv_path, "é", encoding=encoding)

    assert result == "è"


def test_get_key_none(dotenv_path):
    logger = logging.getLogger("dotenv.main")
    dotenv_path.write_text("foo")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.get_key(dotenv_path, "foo")

    assert result is None
    mock_warning.assert_not_called()


def test_unset_with_value(dotenv_path):
    logger = logging.getLogger("dotenv.main")
    dotenv_path.write_text("a=b\nc=d")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.unset_key(dotenv_path, "a")

    assert result == (True, "a")
    assert dotenv_path.read_text() == "c=d"
    mock_warning.assert_not_called()


def test_unset_no_value(dotenv_path):
    logger = logging.getLogger("dotenv.main")
    dotenv_path.write_text("foo")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.unset_key(dotenv_path, "foo")

    assert result == (True, "foo")
    assert dotenv_path.read_text() == ""
    mock_warning.assert_not_called()


def test_unset_encoding(dotenv_path):
    encoding = "latin-1"
    dotenv_path.write_text("é=x", encoding=encoding)

    result = dotenv.unset_key(dotenv_path, "é", encoding=encoding)

    assert result == (True, "é")
    assert dotenv_path.read_text(encoding=encoding) == ""


def test_unset_non_existent_file(tmp_path):
    nx_path = tmp_path / "nx"
    logger = logging.getLogger("dotenv.main")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.unset_key(nx_path, "foo")

    assert result == (None, "foo")
    mock_warning.assert_called_once_with(
        "Can't delete from %s - it doesn't exist.",
        nx_path,
    )


@pytest.mark.skipif(
    sys.platform == "win32", reason="symlinks require elevated privileges on Windows"
)
def test_unset_key_symlink_to_existing_file(tmp_path):
    target = tmp_path / "target.env"
    target.write_text("a=x\n")
    symlink = tmp_path / ".env"
    symlink.symlink_to(target)

    dotenv.unset_key(symlink, "a")

    assert target.read_text() == "a=x\n"
    assert not symlink.is_symlink()
    assert symlink.read_text() == ""


@pytest.mark.skipif(
    sys.platform == "win32", reason="symlinks require elevated privileges on Windows"
)
def test_unset_key_symlink_to_missing_file(tmp_path):
    target = tmp_path / "nx"
    symlink = tmp_path / ".env"
    symlink.symlink_to(target)
    logger = logging.getLogger("dotenv.main")

    with mock.patch.object(logger, "warning") as mock_warning:
        result = dotenv.unset_key(symlink, "a")

    assert result == (None, "a")
    assert symlink.is_symlink()
    mock_warning.assert_called_once()


@pytest.mark.skipif(
    sys.platform == "win32", reason="symlinks require elevated privileges on Windows"
)
def test_unset_key_follow_symlinks(tmp_path):
    target = tmp_path / "target.env"
    target.write_text("a=b\n")
    symlink = tmp_path / ".env"
    symlink.symlink_to(target)

    dotenv.unset_key(symlink, "a", follow_symlinks=True)

    assert target.read_text() == ""
    assert symlink.is_symlink()


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

    leaf = path / "child1" / "child2" / "child3" / "child4"
    leaf.mkdir(parents=True, exist_ok=True)
    return leaf


def test_find_dotenv_no_file_raise(tmp_path):
    leaf = prepare_file_hierarchy(tmp_path)
    os.chdir(leaf)

    with pytest.raises(IOError):
        dotenv.find_dotenv(raise_error_if_not_found=True, usecwd=True)


def test_find_dotenv_no_file_no_raise(tmp_path):
    leaf = prepare_file_hierarchy(tmp_path)
    os.chdir(leaf)

    result = dotenv.find_dotenv(usecwd=True)

    assert result == ""


def test_find_dotenv_found(tmp_path):
    leaf = prepare_file_hierarchy(tmp_path)
    os.chdir(leaf)
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_bytes(b"TEST=test\n")

    result = dotenv.find_dotenv(usecwd=True)

    assert result == str(dotenv_path)


@pytest.mark.skipif(
    sys.platform == "win32", reason="This test assumes case-sensitive variable names"
)
@mock.patch.dict(os.environ, {}, clear=True)
def test_load_dotenv_existing_file(dotenv_path):
    dotenv_path.write_text("a=b")

    result = dotenv.load_dotenv(dotenv_path)

    assert result is True
    assert os.environ == {"a": "b"}


@pytest.mark.parametrize(
    "flag_value",
    [
        "true",
        "yes",
        "1",
        "t",
        "y",
        "True",
        "Yes",
        "TRUE",
        "YES",
        "T",
        "Y",
    ],
)
def test_load_dotenv_disabled(dotenv_path, flag_value):
    expected_environ = {"PYTHON_DOTENV_DISABLED": flag_value}
    with mock.patch.dict(
        os.environ, {"PYTHON_DOTENV_DISABLED": flag_value}, clear=True
    ):
        dotenv_path.write_text("a=b")

        result = dotenv.load_dotenv(dotenv_path)

        assert result is False
        assert os.environ == expected_environ


@pytest.mark.parametrize(
    "flag_value",
    [
        "true",
        "yes",
        "1",
        "t",
        "y",
        "True",
        "Yes",
        "TRUE",
        "YES",
        "T",
        "Y",
    ],
)
def test_load_dotenv_disabled_notification(dotenv_path, flag_value):
    with mock.patch.dict(
        os.environ, {"PYTHON_DOTENV_DISABLED": flag_value}, clear=True
    ):
        dotenv_path.write_text("a=b")

        logger = logging.getLogger("dotenv.main")
        with mock.patch.object(logger, "debug") as mock_debug:
            result = dotenv.load_dotenv(dotenv_path)

        assert result is False
        mock_debug.assert_called_once_with(
            "python-dotenv: .env loading disabled by PYTHON_DOTENV_DISABLED environment variable"
        )


@pytest.mark.skipif(
    sys.platform == "win32", reason="This test assumes case-sensitive variable names"
)
@pytest.mark.parametrize(
    "flag_value",
    [
        "",
        "false",
        "no",
        "0",
        "f",
        "n",
        "False",
        "No",
        "FALSE",
        "NO",
        "F",
        "N",
    ],
)
def test_load_dotenv_enabled(dotenv_path, flag_value):
    expected_environ = {"PYTHON_DOTENV_DISABLED": flag_value, "a": "b"}
    with mock.patch.dict(
        os.environ, {"PYTHON_DOTENV_DISABLED": flag_value}, clear=True
    ):
        dotenv_path.write_text("a=b")

        result = dotenv.load_dotenv(dotenv_path)

        assert result is True
        assert os.environ == expected_environ


@pytest.mark.parametrize(
    "flag_value",
    [
        "",
        "false",
        "no",
        "0",
        "f",
        "n",
        "False",
        "No",
        "FALSE",
        "NO",
        "F",
        "N",
    ],
)
def test_load_dotenv_enabled_no_notification(dotenv_path, flag_value):
    with mock.patch.dict(
        os.environ, {"PYTHON_DOTENV_DISABLED": flag_value}, clear=True
    ):
        dotenv_path.write_text("a=b")

        logger = logging.getLogger("dotenv.main")
        with mock.patch.object(logger, "debug") as mock_debug:
            result = dotenv.load_dotenv(dotenv_path)

        assert result is True
        mock_debug.assert_not_called()


@mock.patch.dict(os.environ, {}, clear=True)
def test_load_dotenv_doesnt_disable_itself(dotenv_path):
    dotenv_path.write_text("PYTHON_DOTENV_DISABLED=true")

    result = dotenv.load_dotenv(dotenv_path)

    assert result is True
    assert os.environ == {"PYTHON_DOTENV_DISABLED": "true"}


def test_load_dotenv_no_file_verbose():
    logger = logging.getLogger("dotenv.main")

    with mock.patch.object(logger, "info") as mock_info:
        result = dotenv.load_dotenv(".does_not_exist", verbose=True)

    assert result is False
    mock_info.assert_called_once_with(
        "python-dotenv could not find configuration file %s.", ".does_not_exist"
    )


@pytest.mark.skipif(
    sys.platform == "win32", reason="This test assumes case-sensitive variable names"
)
@mock.patch.dict(os.environ, {"a": "c"}, clear=True)
def test_load_dotenv_existing_variable_no_override(dotenv_path):
    dotenv_path.write_text("a=b")

    result = dotenv.load_dotenv(dotenv_path, override=False)

    assert result is True
    assert os.environ == {"a": "c"}


@pytest.mark.skipif(
    sys.platform == "win32", reason="This test assumes case-sensitive variable names"
)
@mock.patch.dict(os.environ, {"a": "c"}, clear=True)
def test_load_dotenv_existing_variable_override(dotenv_path):
    dotenv_path.write_text("a=b")

    result = dotenv.load_dotenv(dotenv_path, override=True)

    assert result is True
    assert os.environ == {"a": "b"}


@pytest.mark.skipif(
    sys.platform == "win32", reason="This test assumes case-sensitive variable names"
)
@mock.patch.dict(os.environ, {"a": "c"}, clear=True)
def test_load_dotenv_redefine_var_used_in_file_no_override(dotenv_path):
    dotenv_path.write_text('a=b\nd="${a}"')

    result = dotenv.load_dotenv(dotenv_path)

    assert result is True
    assert os.environ == {"a": "c", "d": "c"}


@pytest.mark.skipif(
    sys.platform == "win32", reason="This test assumes case-sensitive variable names"
)
@mock.patch.dict(os.environ, {"a": "c"}, clear=True)
def test_load_dotenv_redefine_var_used_in_file_with_override(dotenv_path):
    dotenv_path.write_text('a=b\nd="${a}"')

    result = dotenv.load_dotenv(dotenv_path, override=True)

    assert result is True
    assert os.environ == {"a": "b", "d": "b"}


@pytest.mark.skipif(
    sys.platform == "win32", reason="This test assumes case-sensitive variable names"
)
@mock.patch.dict(os.environ, {}, clear=True)
def test_load_dotenv_string_io_utf_8():
    stream = io.StringIO("a=à")

    result = dotenv.load_dotenv(stream=stream)

    assert result is True
    assert os.environ == {"a": "à"}


@pytest.mark.skipif(
    sys.platform == "win32", reason="This test assumes case-sensitive variable names"
)
@mock.patch.dict(os.environ, {}, clear=True)
def test_load_dotenv_file_stream(dotenv_path):
    dotenv_path.write_text("a=b")

    with dotenv_path.open() as f:
        result = dotenv.load_dotenv(stream=f)

    assert result is True
    assert os.environ == {"a": "b"}


def test_load_dotenv_in_current_dir(tmp_path):
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_bytes(b"a=b")
    code_path = tmp_path / "code.py"
    code_path.write_text(
        textwrap.dedent("""
        import dotenv
        import os

        dotenv.load_dotenv(verbose=True)
        print(os.environ['a'])
    """)
    )
    os.chdir(tmp_path)

    result = subprocess.run(
        [sys.executable, str(code_path)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout == "b\n"


def test_dotenv_values_file(dotenv_path):
    dotenv_path.write_text("a=b")

    result = dotenv.dotenv_values(dotenv_path)

    assert result == {"a": "b"}


@pytest.mark.skipif(
    sys.platform == "win32", reason="This test assumes case-sensitive variable names"
)
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
def test_dotenv_values_string_io(env, string, interpolate, expected):
    with mock.patch.dict(os.environ, env, clear=True):
        stream = io.StringIO(string)
        stream.seek(0)

        result = dotenv.dotenv_values(stream=stream, interpolate=interpolate)

        assert result == expected


def test_dotenv_values_file_stream(dotenv_path):
    dotenv_path.write_text("a=b")

    with dotenv_path.open() as f:
        result = dotenv.dotenv_values(stream=f)

    assert result == {"a": "b"}


@pytest.mark.parametrize(
    "input_text,expected",
    [
        # Basic value replacement
        ("A=hello\nB=world\n", "A=A\nB=B\n"),
        # Key with no value
        ("A\n", "A\n"),
        # Comments and blank lines preserved
        ("# a comment\nA=b\n\nB=c\n", "# a comment\nA=A\n\nB=B\n"),
        # Export prefix preserved
        ("export A=b\n", "export A=A\n"),
    ],
)
def test_generate_template_basic(input_text, expected):
    stream = io.StringIO(input_text)

    result = dotenv.generate_template(stream=stream)

    assert result == expected


def test_generate_template_exclude():
    stream = io.StringIO("A=secret # ::dotenv-template-exclude\nB=ok\n")

    result = dotenv.generate_template(stream=stream)

    assert result == "B=B\n"


def test_generate_template_preserve_strips_directive():
    stream = io.StringIO('A="example" # ::dotenv-template-preserve\n')

    result = dotenv.generate_template(stream=stream)

    assert result == 'A="example"\n'


def test_generate_template_preserve_with_comment():
    stream = io.StringIO('A="example" # useful hint ::dotenv-template-preserve\n')

    result = dotenv.generate_template(stream=stream)

    assert result == 'A="example" # useful hint\n'


def test_generate_template_keep_directives():
    stream = io.StringIO(
        'A="example" # ::dotenv-template-preserve\nB=secret # ::dotenv-template-exclude\nC=val\n'
    )

    result = dotenv.generate_template(stream=stream, keep_directives=True)

    assert result == 'A="example" # ::dotenv-template-preserve\nC=C\n'


def test_generate_template_file(dotenv_path):
    dotenv_path.write_text("A=hello\nB=world\n")

    result = dotenv.generate_template(dotenv_path=dotenv_path)

    assert result == "A=A\nB=B\n"


def test_generate_template_empty():
    stream = io.StringIO("")

    result = dotenv.generate_template(stream=stream)

    assert result == ""
