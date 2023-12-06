import io

import pytest

from dotenv.parser import Binding, Original, ValuePart, parse_stream


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("", []),
        (
            "a=b",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="a=b", line=1),
                    error=False,
                )
            ],
        ),
        (
            "'a'=b",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="'a'=b", line=1),
                    error=False,
                )
            ],
        ),
        (
            "[=b",
            [
                Binding(
                    key="[",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="[=b", line=1),
                    error=False,
                )
            ],
        ),
        (
            " a = b ",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string=" a = b ", line=1),
                    error=False,
                )
            ],
        ),
        (
            "export a=b",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="export a=b", line=1),
                    error=False,
                )
            ],
        ),
        (
            " export 'a'=b",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string=" export 'a'=b", line=1),
                    error=False,
                )
            ],
        ),
        (
            "# a=b",
            [
                Binding(
                    key=None,
                    value=None,
                    original=Original(string="# a=b", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a=b#c",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b#c")],
                    original=Original(string="a=b#c", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a=b #c",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="a=b #c", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a=b\t#c",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="a=b\t#c", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a=b c",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b c")],
                    original=Original(string="a=b c", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a=b\tc",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b\tc")],
                    original=Original(string="a=b\tc", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a=b  c",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b  c")],
                    original=Original(string="a=b  c", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a=b\u00a0 c",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b\u00a0 c")],
                    original=Original(string="a=b\u00a0 c", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a=b c ",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b c")],
                    original=Original(string="a=b c ", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a='b c '",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote="'", value="b c ")],
                    original=Original(string="a='b c '", line=1),
                    error=False,
                )
            ],
        ),
        (
            'a="b c "',
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote='"', value="b c ")],
                    original=Original(string='a="b c "', line=1),
                    error=False,
                )
            ],
        ),
        (
            "export export_a=1",
            [
                Binding(
                    key="export_a",
                    value=[ValuePart(quote=None, value="1")],
                    original=Original(string="export export_a=1", line=1),
                    error=False,
                )
            ],
        ),
        (
            "export port=8000",
            [
                Binding(
                    key="port",
                    value=[ValuePart(quote=None, value="8000")],
                    original=Original(string="export port=8000", line=1),
                    error=False,
                )
            ],
        ),
        (
            'a="b\nc"',
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote='"', value="b\nc")],
                    original=Original(string='a="b\nc"', line=1),
                    error=False,
                )
            ],
        ),
        (
            "a='b\nc'",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote="'", value="b\nc")],
                    original=Original(string="a='b\nc'", line=1),
                    error=False,
                )
            ],
        ),
        (
            'a="b\nc"',
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote='"', value="b\nc")],
                    original=Original(string='a="b\nc"', line=1),
                    error=False,
                )
            ],
        ),
        (
            'a="b\\nc"',
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote='"', value="b\nc")],
                    original=Original(string='a="b\\nc"', line=1),
                    error=False,
                )
            ],
        ),
        (
            "a='b\\nc'",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote="'", value="b\\nc")],
                    original=Original(string="a='b\\nc'", line=1),
                    error=False,
                )
            ],
        ),
        (
            'a="b\\"c"',
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote='"', value='b"c')],
                    original=Original(string='a="b\\"c"', line=1),
                    error=False,
                )
            ],
        ),
        (
            "a='b\\'c'",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote="'", value="b'c")],
                    original=Original(string="a='b\\'c'", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a=à",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="à")],
                    original=Original(string="a=à", line=1),
                    error=False,
                )
            ],
        ),
        (
            'a="à"',
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote='"', value="à")],
                    original=Original(string='a="à"', line=1),
                    error=False,
                )
            ],
        ),
        (
            "no_value_var",
            [
                Binding(
                    key="no_value_var",
                    value=None,
                    original=Original(string="no_value_var", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a: b",
            [
                Binding(
                    key=None,
                    value=None,
                    original=Original(string="a: b", line=1),
                    error=True,
                )
            ],
        ),
        (
            "a=b\nc=d",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="a=b\n", line=1),
                    error=False,
                ),
                Binding(
                    key="c",
                    value=[ValuePart(quote=None, value="d")],
                    original=Original(string="c=d", line=2),
                    error=False,
                ),
            ],
        ),
        (
            "a=b\rc=d",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="a=b\r", line=1),
                    error=False,
                ),
                Binding(
                    key="c",
                    value=[ValuePart(quote=None, value="d")],
                    original=Original(string="c=d", line=2),
                    error=False,
                ),
            ],
        ),
        (
            "a=b\r\nc=d",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="a=b\r\n", line=1),
                    error=False,
                ),
                Binding(
                    key="c",
                    value=[ValuePart(quote=None, value="d")],
                    original=Original(string="c=d", line=2),
                    error=False,
                ),
            ],
        ),
        (
            "a=\nb=c",
            [
                Binding(
                    key="a",
                    value=[],
                    original=Original(string="a=\n", line=1),
                    error=False,
                ),
                Binding(
                    key="b",
                    value=[ValuePart(quote=None, value="c")],
                    original=Original(string="b=c", line=2),
                    error=False,
                ),
            ],
        ),
        (
            "\n\n",
            [
                Binding(
                    key=None,
                    value=None,
                    original=Original(string="\n\n", line=1),
                    error=False,
                ),
            ],
        ),
        (
            "a=b\n\n",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="a=b\n", line=1),
                    error=False,
                ),
                Binding(
                    key=None,
                    value=None,
                    original=Original(string="\n", line=2),
                    error=False,
                ),
            ],
        ),
        (
            "a=b\n\nc=d",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="a=b\n", line=1),
                    error=False,
                ),
                Binding(
                    key="c",
                    value=[ValuePart(quote=None, value="d")],
                    original=Original(string="\nc=d", line=2),
                    error=False,
                ),
            ],
        ),
        (
            'a="\nb=c',
            [
                Binding(
                    key=None,
                    value=None,
                    original=Original(string='a="\n', line=1),
                    error=True,
                ),
                Binding(
                    key="b",
                    value=[ValuePart(quote=None, value="c")],
                    original=Original(string="b=c", line=2),
                    error=False,
                ),
            ],
        ),
        (
            '# comment\na="b\nc"\nd=e\n',
            [
                Binding(
                    key=None,
                    value=None,
                    original=Original(string="# comment\n", line=1),
                    error=False,
                ),
                Binding(
                    key="a",
                    value=[ValuePart(quote='"', value="b\nc")],
                    original=Original(string='a="b\nc"\n', line=2),
                    error=False,
                ),
                Binding(
                    key="d",
                    value=[ValuePart(quote=None, value="e")],
                    original=Original(string="d=e\n", line=4),
                    error=False,
                ),
            ],
        ),
        (
            "a=b\n# comment 1",
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="a=b\n", line=1),
                    error=False,
                ),
                Binding(
                    key=None,
                    value=None,
                    original=Original(string="# comment 1", line=2),
                    error=False,
                ),
            ],
        ),
        (
            "# comment 1\n# comment 2",
            [
                Binding(
                    key=None,
                    value=None,
                    original=Original(string="# comment 1\n", line=1),
                    error=False,
                ),
                Binding(
                    key=None,
                    value=None,
                    original=Original(string="# comment 2", line=2),
                    error=False,
                ),
            ],
        ),
        (
            'uglyKey[%$="S3cr3t_P4ssw#rD" #\na=b',
            [
                Binding(
                    key="uglyKey[%$",
                    value=[ValuePart(quote='"', value="S3cr3t_P4ssw#rD")],
                    original=Original(
                        string='uglyKey[%$="S3cr3t_P4ssw#rD" #\n', line=1
                    ),
                    error=False,
                ),
                Binding(
                    key="a",
                    value=[ValuePart(quote=None, value="b")],
                    original=Original(string="a=b", line=2),
                    error=False,
                ),
            ],
        ),
        (
            "a=aa\"bc\"'xx'",
            [
                Binding(
                    key="a",
                    value=[
                        ValuePart(quote=None, value="aa"),
                        ValuePart(quote='"', value="bc"),
                        ValuePart(quote="'", value="xx"),
                    ],
                    original=Original(string="a=aa\"bc\"'xx'", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a = aa \"b\nc\" 'xx'",
            [
                Binding(
                    key="a",
                    value=[
                        ValuePart(quote=None, value="aa "),
                        ValuePart(quote='"', value="b\nc"),
                        ValuePart(quote=None, value=" "),
                        ValuePart(quote="'", value="xx"),
                    ],
                    original=Original(string="a = aa \"b\nc\" 'xx'", line=1),
                    error=False,
                )
            ],
        ),
        (
            "a=\"bc\"'xx'    #comment",
            [
                Binding(
                    key="a",
                    value=[
                        ValuePart(quote='"', value="bc"),
                        ValuePart(quote="'", value="xx"),
                    ],
                    original=Original(string="a=\"bc\"'xx'    #comment", line=1),
                    error=False,
                )
            ],
        ),
        (
            'a="bc"xx  \t #comment',
            [
                Binding(
                    key="a",
                    value=[
                        ValuePart(quote='"', value="bc"),
                        ValuePart(quote=None, value="xx"),
                    ],
                    original=Original(string='a="bc"xx  \t #comment', line=1),
                    error=False,
                )
            ],
        ),
        (
            'a="bc"#comment',
            [
                Binding(
                    key="a",
                    value=[
                        ValuePart(quote='"', value="bc"),
                        ValuePart(quote=None, value="#comment"),
                    ],
                    original=Original(string='a="bc"#comment', line=1),
                    error=False,
                )
            ],
        ),
        (
            'a="bc" #comment"ups"',
            [
                Binding(
                    key="a",
                    value=[ValuePart(quote='"', value="bc")],
                    original=Original(string='a="bc" #comment"ups"', line=1),
                    error=False,
                )
            ],
        ),
    ],
)
def test_parse_stream(test_input, expected):
    result = parse_stream(io.StringIO(test_input))

    assert list(result) == expected
