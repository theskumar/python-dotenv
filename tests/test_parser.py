# -*- coding: utf-8 -*-
import pytest

from dotenv.compat import StringIO
from dotenv.parser import Binding, Original, parse_stream


@pytest.mark.parametrize("test_input,expected", [
    (u"", []),
    (u"a=b", [Binding(key=u"a", value=u"b", original=Original(string=u"a=b", line=1))]),
    (u"'a'=b", [Binding(key=u"a", value=u"b", original=Original(string=u"'a'=b", line=1))]),
    (u"[=b", [Binding(key=u"[", value=u"b", original=Original(string=u"[=b", line=1))]),
    (u" a = b ", [Binding(key=u"a", value=u"b", original=Original(string=u" a = b ", line=1))]),
    (u"export a=b", [Binding(key=u"a", value=u"b", original=Original(string=u"export a=b", line=1))]),
    (u" export 'a'=b", [Binding(key=u"a", value=u"b", original=Original(string=u" export 'a'=b", line=1))]),
    (u"# a=b", [Binding(key=None, value=None, original=Original(string=u"# a=b", line=1))]),
    (u"a=b#c", [Binding(key=u"a", value=u"b#c", original=Original(string=u"a=b#c", line=1))]),
    (u'a=b # comment', [Binding(key=u"a", value=u"b", original=Original(string=u"a=b # comment", line=1))]),
    (u"a=b space ", [Binding(key=u"a", value=u"b space", original=Original(string=u"a=b space ", line=1))]),
    (u"a='b space '", [Binding(key=u"a", value=u"b space ", original=Original(string=u"a='b space '", line=1))]),
    (u'a="b space "', [Binding(key=u"a", value=u"b space ", original=Original(string=u'a="b space "', line=1))]),
    (
        u"export export_a=1",
        [
            Binding(key=u"export_a", value=u"1", original=Original(string=u"export export_a=1", line=1))
        ],
    ),
    (u"export port=8000", [Binding(key=u"port", value=u"8000", original=Original(string=u"export port=8000", line=1))]),
    (u'a="b\nc"', [Binding(key=u"a", value=u"b\nc", original=Original(string=u'a="b\nc"', line=1))]),
    (u"a='b\nc'", [Binding(key=u"a", value=u"b\nc", original=Original(string=u"a='b\nc'", line=1))]),
    (u'a="b\nc"', [Binding(key=u"a", value=u"b\nc", original=Original(string=u'a="b\nc"', line=1))]),
    (u'a="b\\nc"', [Binding(key=u"a", value=u'b\nc', original=Original(string=u'a="b\\nc"', line=1))]),
    (u"a='b\\nc'", [Binding(key=u"a", value=u'b\\nc', original=Original(string=u"a='b\\nc'", line=1))]),
    (u'a="b\\"c"', [Binding(key=u"a", value=u'b"c', original=Original(string=u'a="b\\"c"', line=1))]),
    (u"a='b\\'c'", [Binding(key=u"a", value=u"b'c", original=Original(string=u"a='b\\'c'", line=1))]),
    (u"a=à", [Binding(key=u"a", value=u"à", original=Original(string=u"a=à", line=1))]),
    (u'a="à"', [Binding(key=u"a", value=u"à", original=Original(string=u'a="à"', line=1))]),
    (u'no_value_var', [Binding(key=u'no_value_var', value=None, original=Original(string=u"no_value_var", line=1))]),
    (
        u"a=b\nc=d",
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\n", line=1)),
            Binding(key=u"c", value=u"d", original=Original(string=u"c=d", line=2)),
        ],
    ),
    (
        u"a=b\rc=d",
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\r", line=1)),
            Binding(key=u"c", value=u"d", original=Original(string=u"c=d", line=2)),
        ],
    ),
    (
        u"a=b\r\nc=d",
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\r\n", line=1)),
            Binding(key=u"c", value=u"d", original=Original(string=u"c=d", line=2)),
        ],
    ),
    (
        u'a=\nb=c',
        [
            Binding(key=u"a", value=u'', original=Original(string=u'a=\n', line=1)),
            Binding(key=u"b", value=u'c', original=Original(string=u"b=c", line=2)),
        ]
    ),
    (
        u'a=b\n\nc=d',
        [
            Binding(key=u"a", value=u"b", original=Original(string=u"a=b\n", line=1)),
            Binding(key=u"c", value=u"d", original=Original(string=u"\nc=d", line=2)),
        ]
    ),
    (
        u'a="\nb=c',
        [
            Binding(key=None, value=None, original=Original(string=u'a="\n', line=1)),
            Binding(key=u"b", value=u"c", original=Original(string=u"b=c", line=2)),
        ]
    ),
    (
        u'# comment\na="b\nc"\nd=e\n',
        [
            Binding(key=None, value=None, original=Original(string=u"# comment\n", line=1)),
            Binding(key=u"a", value=u"b\nc", original=Original(string=u'a="b\nc"\n', line=2)),
            Binding(key=u"d", value=u"e", original=Original(string=u"d=e\n", line=4)),
        ],
    ),
    (
        u'uglyKey[%$=\"S3cr3t_P4ssw#rD\" #\na=b',
        [
            Binding(key=u'uglyKey[%$',
                    value=u'S3cr3t_P4ssw#rD',
                    original=Original(string=u"uglyKey[%$=\"S3cr3t_P4ssw#rD\" #\n", line=1)),
            Binding(key=u"a", value=u"b", original=Original(string=u'a=b', line=2)),
        ],
    ),
])
def test_parse_stream(test_input, expected):
    result = parse_stream(StringIO(test_input))

    assert list(result) == expected
