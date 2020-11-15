import re
from abc import ABCMeta

from .compat import IS_TYPE_CHECKING

if IS_TYPE_CHECKING:
    from typing import Iterator, Mapping, Optional, Pattern, Text


_posix_variable = re.compile(
    r"""
    \$\{
        (?P<name>[^\}:]*)
        (?::-
            (?P<default>[^\}]*)
        )?
    \}
    """,
    re.VERBOSE,
)  # type: Pattern[Text]


class Atom():
    __metaclass__ = ABCMeta

    def __ne__(self, other):
        # type: (object) -> bool
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def resolve(self, env):
        # type: (Mapping[Text, Optional[Text]]) -> Text
        raise NotImplementedError


class Literal(Atom):
    def __init__(self, value):
        # type: (Text) -> None
        self.value = value

    def __repr__(self):
        # type: () -> str
        return "Literal(value={})".format(self.value)

    def __eq__(self, other):
        # type: (object) -> bool
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value

    def __hash__(self):
        # type: () -> int
        return hash((self.__class__, self.value))

    def resolve(self, env):
        # type: (Mapping[Text, Optional[Text]]) -> Text
        return self.value


class Variable(Atom):
    def __init__(self, name, default):
        # type: (Text, Optional[Text]) -> None
        self.name = name
        self.default = default

    def __repr__(self):
        # type: () -> str
        return "Variable(name={}, default={})".format(self.name, self.default)

    def __eq__(self, other):
        # type: (object) -> bool
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.name, self.default) == (other.name, other.default)

    def __hash__(self):
        # type: () -> int
        return hash((self.__class__, self.name, self.default))

    def resolve(self, env):
        # type: (Mapping[Text, Optional[Text]]) -> Text
        default = self.default if self.default is not None else ""
        result = env.get(self.name, default)
        return result if result is not None else ""


def parse_variables(value):
    # type: (Text) -> Iterator[Atom]
    cursor = 0

    for match in _posix_variable.finditer(value):
        (start, end) = match.span()
        name = match.groupdict()["name"]
        default = match.groupdict()["default"]

        if start > cursor:
            yield Literal(value=value[cursor:start])

        yield Variable(name=name, default=default)
        cursor = end

    length = len(value)
    if cursor < length:
        yield Literal(value=value[cursor:length])
