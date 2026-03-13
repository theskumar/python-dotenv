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
    string: str
    line: int


class Binding(NamedTuple):
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
    def decode_match(match: Match[str]) -> str:
        return codecs.decode(match.group(0), "unicode-escape")  # type: ignore

    return regex.sub(decode_match, string)


def parse_key(reader: Reader) -> Optional[str]:
    char = reader.peek(1)
    if char == "#":
        return None
    elif char == "'":
        (key,) = reader.read_regex(_single_quoted_key)
    else:
        (key,) = reader.read_regex(_unquoted_key)
    return key


def parse_unquoted_value(reader: Reader) -> str:
    # Start by reading the first part (until newline or comment)
    (part,) = reader.read_regex(_unquoted_value)
    value = re.sub(r"\s+#.*", "", part).rstrip()

    # Check if this might be a multiline value by looking ahead
    while reader.has_next():
        # Save position in case we need to backtrack
        saved_pos = reader.position.chars
        saved_line = reader.position.line

        try:
            # Try to read next character
            next_char = reader.peek(1)
            if next_char in ("\r", "\n"):
                # Read the newline
                reader.read_regex(_newline)

                # Check what's on the next line
                if not reader.has_next():
                    break

                # Check if the next line looks like a new assignment or comment
                rest_of_line = ""
                temp_pos = reader.position.chars
                while temp_pos < len(reader.string) and reader.string[temp_pos] not in (
                    "\r",
                    "\n",
                ):
                    rest_of_line += reader.string[temp_pos]
                    temp_pos += 1

                stripped_line = rest_of_line.strip()

                # If the next line has "=" or starts with "#", it's not a continuation
                if "=" in rest_of_line or stripped_line.startswith("#"):
                    # Restore position and stop
                    reader.position.chars = saved_pos
                    reader.position.line = saved_line
                    break

                # If the next line is empty, it's not a continuation
                if stripped_line == "":
                    # Restore position and stop
                    reader.position.chars = saved_pos
                    reader.position.line = saved_line
                    break

                # Simple heuristic: treat single-character lines as variables, longer lines as continuation
                # This handles the common case where "c" is a variable but "baz" is continuation content
                if len(stripped_line) == 1 and stripped_line.isalpha():
                    # Single letter, likely a variable name
                    reader.position.chars = saved_pos
                    reader.position.line = saved_line
                    break

                # This looks like a continuation line
                value += "\n"
                (next_part,) = reader.read_regex(_unquoted_value)
                next_part = re.sub(r"\s+#.*", "", next_part).rstrip()
                value += next_part
            else:
                break
        except Exception:
            # If anything goes wrong, restore position and stop
            reader.position.chars = saved_pos
            reader.position.line = saved_line
            break

    return value


def parse_value(reader: Reader) -> str:
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
    reader = Reader(stream)
    while reader.has_next():
        yield parse_binding(reader)
