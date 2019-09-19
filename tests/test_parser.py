# -*- coding: utf-8 -*-
import pytest

from dotenv.compat import StringIO
from dotenv.parser import Binding, parse_stream


@pytest.mark.parametrize("test_input,expected", [
    (u"", []),
    (u"a=b", [Binding(key=u"a", value=u"b", original=u"a=b")]),
    (u"'a'=b", [Binding(key=u"a", value=u"b", original=u"'a'=b")]),
    (u"[=b", [Binding(key=u"[", value=u"b", original=u"[=b")]),
    (u" a = b ", [Binding(key=u"a", value=u"b", original=u" a = b ")]),
    (u"export a=b", [Binding(key=u"a", value=u"b", original=u"export a=b")]),
    (u" export 'a'=b", [Binding(key=u"a", value=u"b", original=u" export 'a'=b")]),
    (u"# a=b", [Binding(key=None, value=None, original=u"# a=b")]),
    (u"a=b#c", [Binding(key=u"a", value=u"b#c", original=u"a=b#c")]),
    (u'a=b # comment', [Binding(key=u"a", value=u"b", original=u"a=b # comment")]),
    (u"a=b space ", [Binding(key=u"a", value=u"b space", original=u"a=b space ")]),
    (u"a='b space '", [Binding(key=u"a", value=u"b space ", original=u"a='b space '")]),
    (u'a="b space "', [Binding(key=u"a", value=u"b space ", original=u'a="b space "')]),
    (u"export export_a=1", [Binding(key=u"export_a", value=u"1", original=u"export export_a=1")]),
    (u"export port=8000", [Binding(key=u"port", value=u"8000", original=u"export port=8000")]),
    (u'a="b\nc"', [Binding(key=u"a", value=u"b\nc", original=u'a="b\nc"')]),
    (u"a='b\nc'", [Binding(key=u"a", value=u"b\nc", original=u"a='b\nc'")]),
    (u'a="b\nc"', [Binding(key=u"a", value=u"b\nc", original=u'a="b\nc"')]),
    (u'a="b\\nc"', [Binding(key=u"a", value=u'b\nc', original=u'a="b\\nc"')]),
    (u"a='b\\nc'", [Binding(key=u"a", value=u'b\\nc', original=u"a='b\\nc'")]),
    (u'a="b\\"c"', [Binding(key=u"a", value=u'b"c', original=u'a="b\\"c"')]),
    (u"a='b\\'c'", [Binding(key=u"a", value=u"b'c", original=u"a='b\\'c'")]),
    (u"a=à", [Binding(key=u"a", value=u"à", original=u"a=à")]),
    (u'a="à"', [Binding(key=u"a", value=u"à", original=u'a="à"')]),
    (u'garbage', [Binding(key=None, value=None, original=u"garbage")]),
    (
        u"a=b\nc=d",
        [
            Binding(key=u"a", value=u"b", original=u"a=b\n"),
            Binding(key=u"c", value=u"d", original=u"c=d"),
        ],
    ),
    (
        u"a=b\r\nc=d",
        [
            Binding(key=u"a", value=u"b", original=u"a=b\r\n"),
            Binding(key=u"c", value=u"d", original=u"c=d"),
        ],
    ),
    (
        u'a=\nb=c',
        [
            Binding(key=u"a", value=u'', original=u'a=\n'),
            Binding(key=u"b", value=u'c', original=u"b=c"),
        ]
    ),
    (
        u'a=b\n\nc=d',
        [
            Binding(key=u"a", value=u"b", original=u"a=b\n"),
            Binding(key=u"c", value=u"d", original=u"\nc=d"),
        ]
    ),
    (
        u'a="\nb=c',
        [
            Binding(key=None, value=None, original=u'a="\n'),
            Binding(key=u"b", value=u"c", original=u"b=c"),
        ]
    ),
    (
        u'# comment\na="b\nc"\nd=e\n',
        [
            Binding(key=None, value=None, original=u"# comment\n"),
            Binding(key=u"a", value=u"b\nc", original=u'a="b\nc"\n'),
            Binding(key=u"d", value=u"e", original=u"d=e\n"),
        ],
    ),
    (
        u'garbage[%$#\na=b',
        [
            Binding(key=None, value=None, original=u"garbage[%$#\n"),
            Binding(key=u"a", value=u"b", original=u'a=b'),
        ],
    ),
])
def test_parse_stream(test_input, expected):
    result = parse_stream(StringIO(test_input))

    assert list(result) == expected
