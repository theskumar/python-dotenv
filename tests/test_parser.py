# -*- coding: utf-8 -*-
import pytest

from dotenv.compat import StringIO
from dotenv.parser import Binding, parse_stream


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
        'a=\nb=c',
        [
            Binding(key="a", value='', original='a=\n'),
            Binding(key="b", value='c', original="b=c"),
        ]
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
