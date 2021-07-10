import io

import pytest

from dotenv.parser import Binding, Original, parse_stream


@pytest.mark.parametrize("test_input,expected", [
    (u"", []),
    (u"a=b", [Binding(key=u"a", value=u"b", original=Original(string=u"a=b", line=1), error=False)]),
    (u"'a'=b", [Binding(key=u"a", value=u"b", original=Original(string=u"'a'=b", line=1), error=False)]),
    (u"[=b", [Binding(key=u"[", value=u"b", original=Original(string=u"[=b", line=1), error=False)]),
    (u" a = b ", [Binding(key=u"a", value=u"b", original=Original(string=u" a = b ", line=1), error=False)]),
    (u"export a=b", [Binding(key=u"a", value=u"b", original=Original(string=u"export a=b", line=1), error=False)]),
    (
        u" export 'a'=b",
        [Binding(key=u"a", value=u"b", original=Original(string=u" export 'a'=b", line=1), error=False)],
    ),
    (u"# a=b", [Binding(key=None, value=None, original=Original(string=u"# a=b", line=1), error=False)]),
    (u"a=b#c", [Binding(key=u"a", value=u"b#c", original=Original(string=u"a=b#c", line=1), error=False)]),
    (
        u'a=b #c',
        [Binding(key=u"a", value=u"b", original=Original(string=u"a=b #c", line=1), error=False)],
    ),
    (
        u'a=b\t#c',
        [Binding(key=u"a", value=u"b", original=Original(string=u"a=b\t#c", line=1), error=False)],
    ),
    (
        u"a=b c",
        [Binding(key=u"a", value=u"b c", original=Original(string=u"a=b c", line=1), error=False)],
    ),
    (
        u"a=b\tc",
        [Binding(key=u"a", value=u"b\tc", original=Original(string=u"a=b\tc", line=1), error=False)],
    ),
    (
        u"a=b  c",
        [Binding(key=u"a", value=u"b  c", original=Original(string=u"a=b  c", line=1), error=False)],
    ),
    (
        u"a=b\u00a0 c",
        [Binding(key=u"a", value=u"b\u00a0 c", original=Original(string=u"a=b\u00a0 c", line=1), error=False)],
    ),
    (
        u"a=b c ",
        [Binding(key=u"a", value=u"b c", original=Original(string=u"a=b c ", line=1), error=False)],
    ),
    (
        u"a='b c '",
        [Binding(key=u"a", value=u"b c ", original=Original(string=u"a='b c '", line=1), error=False)],
    ),
    (
        u'a="b c "',
        [Binding(key=u"a", value=u"b c ", original=Original(string=u'a="b c "', line=1), error=False)],
    ),
    (
        u"export export_a=1",
        [
            Binding(key=u"export_a", value=u"1", original=Original(string=u"export export_a=1", line=1), error=False)
        ],
    ),
    (
        u"export port=8000",
        [Binding(key=u"port", value=u"8000", original=Original(string=u"export port=8000", line=1), error=False)],
    ),
    (u'a="b\nc"', [Binding(key=u"a", value=u"b\nc", original=Original(string=u'a="b\nc"', line=1), error=False)]),
    (u"a='b\nc'", [Binding(key=u"a", value=u"b\nc", original=Original(string=u"a='b\nc'", line=1), error=False)]),
    (u'a="b\nc"', [Binding(key=u"a", value=u"b\nc", original=Original(string=u'a="b\nc"', line=1), error=False)]),
    (u'a="b\\nc"', [Binding(key=u"a", value=u'b\nc', original=Original(string=u'a="b\\nc"', line=1), error=False)]),
    (u"a='b\\nc'", [Binding(key=u"a", value=u'b\\nc', original=Original(string=u"a='b\\nc'", line=1), error=False)]),
    (u'a="b\\"c"', [Binding(key=u"a", value=u'b"c', original=Original(string=u'a="b\\"c"', line=1), error=False)]),
    (u"a='b\\'c'", [Binding(key=u"a", value=u"b'c", original=Original(string=u"a='b\\'c'", line=1), error=False)]),
    (u"a=à", [Binding(key=u"a", value=u"à", original=Original(string=u"a=à", line=1), error=False)]),
    (u'a="à"', [Binding(key=u"a", value=u"à", original=Original(string=u'a="à"', line=1), error=False)]),
    (
        u'no_value_var',
        [Binding(key=u'no_value_var', value=None, original=Original(string=u"no_value_var", line=1), error=False)],
    ),
    (u'a: b', [Binding(key=None, value=None, original=Original(string=u"a: b", line=1), error=True)]),
    (
        u"a=b\nc=d",
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\n", line=1), error=False),
            Binding(key=u"c", value=u"d", original=Original(string=u"c=d", line=2), error=False),
        ],
    ),
    (
        u"a=b\rc=d",
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\r", line=1), error=False),
            Binding(key=u"c", value=u"d", original=Original(string=u"c=d", line=2), error=False),
        ],
    ),
    (
        u"a=b\r\nc=d",
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\r\n", line=1), error=False),
            Binding(key=u"c", value=u"d", original=Original(string=u"c=d", line=2), error=False),
        ],
    ),
    (
        u'a=\nb=c',
        [
            Binding(key=u"a", value=u'', original=Original(string=u'a=\n', line=1), error=False),
            Binding(key=u"b", value=u'c', original=Original(string=u"b=c", line=2), error=False),
        ]
    ),
    (
        u"\n\n",
        [
            Binding(key=None, value=None, original=Original(string=u"\n\n", line=1), error=False),
        ]
    ),
    (
        u"a=b\n\n",
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\n", line=1), error=False),
            Binding(key=None, value=None, original=Original(string=u"\n", line=2), error=False),
        ]
    ),
    (
        u'a=b\n\nc=d',
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\n", line=1), error=False),
            Binding(key=u"c", value=u"d", original=Original(string=u"\nc=d", line=2), error=False),
        ]
    ),
    (
        u'a="\nb=c',
        [
            Binding(key=None, value=None, original=Original(string=u'a="\n', line=1), error=True),
            Binding(key=u"b", value=u"c", original=Original(string=u"b=c", line=2), error=False),
        ]
    ),
    (
        u'# comment\na="b\nc"\nd=e\n',
        [
            Binding(key=None, value=None, original=Original(string=u"# comment\n", line=1), error=False),
            Binding(key=u"a", value=u"b\nc", original=Original(string=u'a="b\nc"\n', line=2), error=False),
            Binding(key=u"d", value=u"e", original=Original(string=u"d=e\n", line=4), error=False),
        ],
    ),
    (
        u'a=b\n# comment 1',
        [
            Binding(key="a", value="b", original=Original(string=u"a=b\n", line=1), error=False),
            Binding(key=None, value=None, original=Original(string=u"# comment 1", line=2), error=False),
        ],
    ),
    (
        u'# comment 1\n# comment 2',
        [
            Binding(key=None, value=None, original=Original(string=u"# comment 1\n", line=1), error=False),
            Binding(key=None, value=None, original=Original(string=u"# comment 2", line=2), error=False),
        ],
    ),
    (
        u'uglyKey[%$=\"S3cr3t_P4ssw#rD\" #\na=b',
        [
            Binding(key=u'uglyKey[%$',
                    value=u'S3cr3t_P4ssw#rD',
                    original=Original(string=u"uglyKey[%$=\"S3cr3t_P4ssw#rD\" #\n", line=1), error=False),
            Binding(key=u"a", value=u"b", original=Original(string=u'a=b', line=2), error=False),
        ],
    ),
])
def test_parse_stream(test_input, expected):
    result = parse_stream(io.StringIO(test_input))

    assert list(result) == expected
