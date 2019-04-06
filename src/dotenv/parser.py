import codecs
import re
from typing import (IO, Iterator, Match, NamedTuple, Optional, Pattern,  # noqa
                    Text, Tuple)

_binding = re.compile(
    r"""
        (
            \s*                     # leading whitespace
            (?:export{0}+)?         # export

            ( '[^']+'               # single-quoted key
            | [^=\#\s]+             # or unquoted key
            )?

            (?:
                (?:{0}*={0}*)       # equal sign

                ( '(?:\\'|[^'])*'   # single-quoted value
                | "(?:\\"|[^"])*"   # or double-quoted value
                | [^\#\r\n]*        # or unquoted value
                )
            )?

            \s*                     # trailing whitespace
            (?:\#[^\r\n]*)?         # comment
            (?:\r|\n|\r\n)?         # newline
        )
    """.format(r'[^\S\r\n]'),
    re.MULTILINE | re.VERBOSE,
)  # type: Pattern[Text]

_escape_sequence = re.compile(r"\\[\\'\"abfnrtv]")  # type: Pattern[Text]


Binding = NamedTuple("Binding", [("key", Optional[Text]),
                                 ("value", Optional[Text]),
                                 ("original", Text)])


def decode_escapes(string):
    # type: (Text) -> Text
    def decode_match(match):
        # type: (Match[Text]) -> Text
        return codecs.decode(match.group(0), 'unicode-escape')  # type: ignore

    return _escape_sequence.sub(decode_match, string)


def is_surrounded_by(string, char):
    # type: (Text, Text) -> bool
    return (
        len(string) > 1
        and string[0] == string[-1] == char
    )


def parse_binding(string, position):
    # type: (Text, int) -> Tuple[Binding, int]
    match = _binding.match(string, position)
    assert match is not None
    (matched, key, value) = match.groups()
    if key is None or value is None:
        key = None
        value = None
    else:
        value_quoted = is_surrounded_by(value, "'") or is_surrounded_by(value, '"')
        if value_quoted:
            value = decode_escapes(value[1:-1])
        else:
            value = value.strip()
    return (Binding(key=key, value=value, original=matched), match.end())


def parse_stream(stream):
    # type:(IO[Text]) -> Iterator[Binding]
    string = stream.read()
    position = 0
    length = len(string)
    while position < length:
        (binding, position) = parse_binding(string, position)
        yield binding
