import codecs
import re
from typing import (
    IO,
    Iterator,
    Match,
    NamedTuple,
    Optional,
    Pattern,
    Sequence,
)


def make_regex(string: str, extra_flags: int = 0) -> Pattern[str]:
    return re.compile(string, re.UNICODE | extra_flags)


_newline = make_regex(r"(\r\n|\n|\r)")
_multiline_whitespace = make_regex(r"\s*", extra_flags=re.MULTILINE)
_whitespace = make_regex(r"[^\S\r\n]*")
_export = make_regex(r"(?:export[^\S\r\n]+)?")
_single_quoted_key = make_regex(r"'([^']+)'")
_unquoted_key = make_regex(r"([^=\#\s]+)")
_equal_sign = make_regex(r"(=[^\S\r\n]*)")
_single_quoted_value = make_regex(r"'((?:\\'|[^'])*)'")
_double_quoted_value = make_regex(r'"((?:\\"|[^"])*)"')
_unquoted_value = make_regex(r"([^\r\n]*)")
_comment = make_regex(r"(?:[^\S\r\n]*#[^\r\n]*)?")
_end_of_line = make_regex(r"[^\S\r\n]*(?:\r\n|\n|\r|$)")
_rest_of_line = make_regex(r"[^\r\n]*(?:\r|\n|\r\n)?")
_double_quote_escapes = make_regex(r"\\[\\'\"abfnrtv]")
_single_quote_escapes = make_regex(r"\\[\\']")


class Original(NamedTuple):
    """Raw text of a parsed line and its 1-based line number."""

    string: str
    line: int


class Binding(NamedTuple):
    """Parsed result for a single line of a ``.env`` file.

    Attributes:
        key: Variable name, or ``None`` for comments, blank lines, and
            unparseable lines.
        value: Assigned value, or ``None`` when the key has no ``=`` sign
            or the line could not be parsed.
        original: The raw text and line number this binding was parsed from.
        error: ``True`` if the line could not be parsed.
    """

    key: Optional[str]
    value: Optional[str]
    original: Original
    error: bool


class Position:
    def __init__(self, chars: int, line: int) -> None:
        self.chars = chars
        self.line = line

    @classmethod
    def start(cls) -> "Position":
        return cls(chars=0, line=1)

    def set(self, other: "Position") -> None:
        self.chars = other.chars
        self.line = other.line

    def advance(self, string: str) -> None:
        self.chars += len(string)
        self.line += len(re.findall(_newline, string))


class Error(Exception):
    pass


class Reader:
    """Stateful reader that consumes a ``.env`` stream character by character."""

    def __init__(self, stream: IO[str]) -> None:
        self.string = stream.read()
        self.position = Position.start()
        self.mark = Position.start()

    def has_next(self) -> bool:
        return self.position.chars < len(self.string)

    def set_mark(self) -> None:
        self.mark.set(self.position)

    def get_marked(self) -> Original:
        return Original(
            string=self.string[self.mark.chars : self.position.chars],
            line=self.mark.line,
        )

    def peek(self, count: int) -> str:
        return self.string[self.position.chars : self.position.chars + count]

    def read(self, count: int) -> str:
        result = self.string[self.position.chars : self.position.chars + count]
        if len(result) < count:
            raise Error("read: End of string")
        self.position.advance(result)
        return result

    def read_regex(self, regex: Pattern[str]) -> Sequence[str]:
        match = regex.match(self.string, self.position.chars)
        if match is None:
            raise Error("read_regex: Pattern not found")
        self.position.advance(self.string[match.start() : match.end()])
        return match.groups()


def decode_escapes(regex: Pattern[str], string: str) -> str:
    """Replace escape sequences matched by *regex* with their decoded characters."""

    def decode_match(match: Match[str]) -> str:
        return codecs.decode(match.group(0), "unicode-escape")  # type: ignore

    return regex.sub(decode_match, string)


def parse_key(reader: Reader) -> Optional[str]:
    """Parse and return the key portion of a binding, or ``None`` for comments."""
    char = reader.peek(1)
    if char == "#":
        return None
    elif char == "'":
        (key,) = reader.read_regex(_single_quoted_key)
    else:
        (key,) = reader.read_regex(_unquoted_key)
    return key


def parse_unquoted_value(reader: Reader) -> str:
    """Parse an unquoted value, stripping inline comments and trailing whitespace."""
    (part,) = reader.read_regex(_unquoted_value)
    return re.sub(r"\s+#.*", "", part).rstrip()


def parse_value(reader: Reader) -> str:
    """Parse a value that may be single-quoted, double-quoted, or unquoted."""
    char = reader.peek(1)
    if char == "'":
        (value,) = reader.read_regex(_single_quoted_value)
        return decode_escapes(_single_quote_escapes, value)
    elif char == '"':
        (value,) = reader.read_regex(_double_quoted_value)
        return decode_escapes(_double_quote_escapes, value)
    elif char in ("", "\n", "\r"):
        return ""
    else:
        return parse_unquoted_value(reader)


def parse_binding(reader: Reader) -> Binding:
    """Parse the next complete binding (key-value pair, comment, or blank line)."""
    reader.set_mark()
    try:
        reader.read_regex(_multiline_whitespace)
        if not reader.has_next():
            return Binding(
                key=None,
                value=None,
                original=reader.get_marked(),
                error=False,
            )
        reader.read_regex(_export)
        key = parse_key(reader)
        reader.read_regex(_whitespace)
        if reader.peek(1) == "=":
            reader.read_regex(_equal_sign)
            value: Optional[str] = parse_value(reader)
        else:
            value = None
        reader.read_regex(_comment)
        reader.read_regex(_end_of_line)
        return Binding(
            key=key,
            value=value,
            original=reader.get_marked(),
            error=False,
        )
    except Error:
        reader.read_regex(_rest_of_line)
        return Binding(
            key=None,
            value=None,
            original=reader.get_marked(),
            error=True,
        )


def parse_stream(stream: IO[str]) -> Iterator[Binding]:
    """Yield :class:`Binding` instances for every line in a ``.env`` stream."""
    reader = Reader(stream)
    while reader.has_next():
        yield parse_binding(reader)
